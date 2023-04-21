from fastapi import FastAPI, WebSocket, HTTPException, Body
from resources.data_collection import Order, DB, active_websockets, broadcast_db_change
import asyncio


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/orders')
async def get_orders():
    return DB


@app.post('/orders')
async def post_order(payload: dict = Body(...)):
    if not str(payload['stocks']).isalpha() or (not isinstance(payload['quantity'], int) or payload['quantity'] <= 0):
        raise HTTPException(status_code=400, detail="Invalid payload!")
    order = Order(payload['stocks'],  payload['quantity'], asyncio.get_event_loop())
    DB[order.order_id] = order.info()
    await broadcast_db_change("Order created", order.info())

    return {"message": "Order created successfully",
            "order_id": int(order.order_id)}


@app.get('/orders/<order_id: int>')
def get_order_by_id(order_id):
    try:
        return DB[order_id]
    except KeyError:
        return HTTPException(status_code=404, detail=f"Requested order {order_id} does not exist!")


@app.delete('/orders/{order_id}')
async def delete_order_by_id(order_id: int):
    try:
        deleted_order = DB[order_id]
        del DB[order_id]
        await broadcast_db_change("Order deleted", deleted_order)
        return {"message": f"Order {order_id} deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Requested order {order_id} does not exist!")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except:
        pass
    finally:
        active_websockets.remove(websocket)

