import json

import pytest
import requests
import asyncio

from conftest import URL, check_invalid_payload, valid_order_data, invalid_order_data, assert_order_created, \
    assert_order_deleted


def test_place_correct_order():
    r = requests.post("http://127.0.0.1:8000/orders", json={"stocks": "test",
                                                            "quantity": 1})
    assert r.status_code == 200
    assert r.json()["message"] == "Order created successfully"
    assert str(r.json()["order_id"]).isnumeric()


def test_place_incorrect_order():
    check_invalid_payload(requests.post(URL, json={"stocks": "test",
                                                   "quantity": -1}))

    check_invalid_payload(requests.post(URL, json={"stocks": 11,
                                                   "quantity": 12}))


@pytest.mark.asyncio
@pytest.mark.parametrize("expected_status_code", [200, 400])
async def test_order_updates(async_client, ws_client, expected_status_code):
    response = await async_client.post(URL,
                                       json=valid_order_data if expected_status_code == 200 else invalid_order_data)
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        order_id = response.json()["order_id"]
        message_data = json.loads(await ws_client.recv())
        assert_order_created(message_data, order_id)

        response = await async_client.delete(f"{URL}/{order_id}")
        assert response.status_code == 200

        message_data = json.loads(await ws_client.recv())
        assert_order_deleted(message_data, order_id)
        pass
    else:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(ws_client.recv(), timeout=1)
