import pytest
import websockets
import httpx
import asyncio


URL = "http://127.0.0.1:8000/orders"
WS = f"ws://127.0.0.1:8000/ws"
valid_order_data = {"stocks": "AAPL", "quantity": 10}
invalid_order_data = {"stocks": "AAPL", "quantity": "ten"}


def check_invalid_payload(response):
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid payload!"
    }


@pytest.fixture(scope="function", autouse=False)
def assert_order_created(message_data, order_id):
    assert message_data["action"] == "Order created successfully"
    assert message_data["order"]["order_id"] == order_id


@pytest.fixture(scope="function", autouse=False)
def assert_order_deleted(message_data, order_id):
    assert message_data["action"] == "Order deleted"
    assert message_data["order"]["order_id"] == order_id


@pytest.fixture(scope="function", autouse=False)
async def assert_order_not_created(ws_client):
    async with ws_client:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(ws_client.recv(), timeout=1)


@pytest.fixture(scope="function", autouse=False)
async def async_client():
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
async def ws_client():
    async with websockets.connect(WS) as ws:
        yield ws
