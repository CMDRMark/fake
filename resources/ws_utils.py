active_websockets = []


async def broadcast_db_change(message: str, order_info: dict):
    change_info = {"message": message, "order": order_info}
    for websocket in active_websockets:
        await websocket.send_json(change_info)
