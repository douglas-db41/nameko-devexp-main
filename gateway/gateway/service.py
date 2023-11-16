import json

from marshmallow import ValidationError
from nameko import config
from nameko.exceptions import BadRequest
from nameko.rpc import RpcProxy
from werkzeug import Response

from gateway.entrypoints import http
from gateway.exceptions import OrderNotFound, ProductNotFound, ProductInUse
from gateway.schemas import CreateOrderSchema, GetOrderSchema, ProductSchema


class GatewayService(object):
    """
    Service acts as a gateway to other services over http.
    """

    name = 'gateway'

    orders_rpc = RpcProxy('orders')
    products_rpc = RpcProxy('products')

    @http(
        "GET", "/products/<string:product_id>",
        expected_exceptions=ProductNotFound
    )
    def get_product(self, request, product_id):
        """Gets product by `product_id`
        """
        product = self.products_rpc.get(product_id)
        return Response(
            ProductSchema().dumps(product),
            mimetype='application/json'
        )

    @http(
        "POST", "/products",
        expected_exceptions=(ValidationError, BadRequest)
    )
    def create_product(self, request):
        """Create a new product - product data is posted as json

        Example request ::

            {
                "id": "the_odyssey",
                "title": "The Odyssey",
                "passenger_capacity": 101,
                "maximum_speed": 5,
                "in_stock": 10
            }


        The response contains the new product ID in a json document ::

            {"id": "the_odyssey"}

        """

        schema = ProductSchema()

        try:
            # load input data through a schema (for validation)
            # Note - this may raise `ValueError` for invalid json,
            # or `ValidationError` if data is invalid.
            product_data = schema.loads(request.get_data(as_text=True))
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        # Create the product
        self.products_rpc.create(product_data)
        return Response(
            json.dumps({'id': product_data['id']}), mimetype='application/json'
        )

    @http("GET", "/orders/<int:order_id>", expected_exceptions=OrderNotFound)
    def get_order(self, request, order_id):
        """Gets the order details for the order given by `order_id`.

        Enhances the order details with full product details from the
        products-service.
        """
        order = self._get_order(order_id)
        return Response(
            GetOrderSchema().dumps(order),
            mimetype='application/json'
        )

    def _get_order(self, order_id):
        # Retrieve order data from the orders service.
        # Note - this may raise a remote exception that has been mapped to
        # raise``OrderNotFound``
        order = self.orders_rpc.get_order(order_id)

        for item in order['order_details']:
            product_id = item['product_id']
            # Construct an image url.
            item['image'] = '{}/{}.jpg'.format(config['PRODUCT_IMAGE_ROOT'], product_id)

        return order

    @http(
        "POST", "/orders",
        expected_exceptions=(ValidationError, ProductNotFound, BadRequest)
    )
    def create_order(self, request):
        """Create a new order - order data is posted as json

        Example request ::

            {
                "order_details": [
                    {
                        "product_id": "the_odyssey",
                        "price": "99.99",
                        "quantity": 1
                    },
                    {
                        "price": "5.99",
                        "product_id": "the_enigma",
                        "quantity": 2
                    },
                ]
            }


        The response contains the new order ID in a json document ::

            {"id": 1234}

        """

        schema = CreateOrderSchema()

        try:
            # load input data through a schema (for validation)
            # Note - this may raise `ValueError` for invalid json,
            # or `ValidationError` if data is invalid.
            order_data = schema.loads(request.get_data(as_text=True))
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        # Create the order
        # Note - this may raise `ProductNotFound`
        id_ = self._create_order(order_data)
        return Response(json.dumps({'id': id_}), mimetype='application/json')

    def _create_order(self, order_data):
        # check order product ids are valid
        valid_product_ids = {prod['id'] for prod in self.products_rpc.list()}
        for item in order_data['order_details']:
            if item['product_id'] not in valid_product_ids:
                raise ProductNotFound(
                    "Product Id {}".format(item['product_id'])
                )

        # Call orders-service to create the order.
        # Dump the data through the schema to ensure the values are serialized
        # correctly.
        serialized_data = CreateOrderSchema().dump(order_data)
        result = self.orders_rpc.create_order(
            serialized_data['order_details']
        )
        return result['id']

    @http(
        "DELETE", "/products/<string:product_id>",
        expected_exceptions=(ProductNotFound, ProductInUse)
    )
    def delete_product(self, request, product_id):
        """Deletes a product with the given `product_id`
        """
        try:
            self.products_rpc.delete(product_id)
        except remote_error as error:
            if error.exc_type == 'ProductInUse':
                raise ProductInUse(str(error.value))
            elif error.exc_type == 'ProductNotFound':
                raise ProductNotFound(str(error.value))

        return Response(status=204)

    @http("GET", "/orders")
    def list_orders(self, request):
        """List all orders
        """
        # Call orders-service to retrieve the data
        orders = self._list_orders()
        return Response(OrderSchema().dumps(orders), mimetype='application/json')

    def _list_orders(self):
        with self.orders_rpc.next() as nameko:
            orders = nameko.orders.list_orders()
        return orders