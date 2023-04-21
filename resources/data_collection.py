from random import randint
import asyncio
from random import uniform
from resources.ws_utils import broadcast_db_change, active_websockets

DB = {}


class Order:

    def __init__(self, stock, quantity, event_loop):
        self.order_id = randint(1000, 9999)
        self.status = "Pending"
        self.stock = stock
        self.quantity = quantity
        event_loop.create_task(execute_order(self))

    def get_status(self):
        return self.status

    def info(self):
        return {
            "order_id": self.order_id,
            "status": self.status,
            "stock": self.stock,
            "quantity": self.quantity,
        }


async def execute_order(order):
    await asyncio.sleep(uniform(0.1, 1))
    order.status = "Executed"
    DB[order.order_id] = order.info()
    await broadcast_db_change("Order executed", order.info())