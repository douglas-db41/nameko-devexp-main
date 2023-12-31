import logging

from nameko.events import event_handler
from nameko.rpc import rpc
from nameko.rpc import RpcProxy

from products import dependencies, schemas
from products.exceptions import ProductInUse

logger = logging.getLogger(__name__)


class ProductsService:

    name = 'products'

    storage = dependencies.Storage()

    orders_rpc = RpcProxy('orders')

    @rpc
    def get(self, product_id):
        product = self.storage.get(product_id)
        return schemas.Product().dump(product)

    @rpc
    def list(self):
        products = self.storage.list()
        return schemas.Product(many=True).dump(products)

    @rpc
    def create(self, product):
        product = schemas.Product().load(product)
        self.storage.create(product)
    
    @rpc
    def delete(self, product_id):
        if self._is_product_in_use(product_id):
            raise ProductInUse(f'Product with id {product_id} is in use and cannot be deleted')
        self.storage.delete(product_id)

    @event_handler('orders', 'order_created')
    def handle_order_created(self, payload):
        for product in payload['order']['order_details']:
            self.storage.decrement_stock(
                product['product_id'], product['quantity'])

    def _is_product_in_use(self, product_id):
        return len(self.orders_rpc.list_orders_by_product_id(product_id)) > 0