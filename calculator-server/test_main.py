from fastapi.testclient import TestClient
from main import app  # or whatever your app module is
import time

client = TestClient(app)


def test_basic_division():
    r = client.post("/calculate", json={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9
    assert data["error"] == ""    #new assert lab03

def test_percent_subtraction():
    r = client.post("/calculate", json={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", json={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = client.post("/calculate", json={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""
    assert data["result"] == ""    #new assert lab03


# TODO Add more tests

def clear_history_list():
    client.delete("/history")   # write function so the item doesn't accumulate

# TEST CASE , post calculate
def test_basic_addition():
    post_result = client.post("/calculate", json={"expr": "999+999"})
    assert post_result.status_code == 200
    data = post_result.json()
    assert data["ok"] is True
    assert data["result"] == 1998
    assert "error" not in data or data["error"] == ""
    clear_history_list()

def test_basic_multiplication():
    post_result = client.post("/calculate", json={"expr": "999*999"})
    assert post_result.status_code == 200
    data = post_result.json()
    assert data["ok"] is True
    assert data["result"] == 998001
    assert "error" not in data or data["error"] == ""
    clear_history_list()

def test_basic_exponent():
    post_result = client.post("/calculate", json={"expr": "9**9"})
    assert post_result.status_code == 200
    data = post_result.json()
    assert data["ok"] is True
    assert data["result"] == 387420489
    assert "error" not in data or data["error"] == "" 
    clear_history_list()

# TEST CASE , get history

def test_get_history_returns_all_records():
    clear_history_list()
    client.post("/calculate", json={"expr": "1+1"})
    time.sleep(0.01)
    client.post("/calculate", json={"expr": "2*3"})
    get_result = client.get("/history")
    assert get_result.status_code == 200
    data = get_result.json()
    assert len(data) == 2
    assert data[0]["expr"] == "2*3"
    assert data[0]["result"] == 6
    assert data[1]["expr"] == "1+1"
    assert data[1]["result"] == 2
    assert "timestamp" in data[0]
    assert "timestamp" in data[1]    #new assert lab03


def test_get_history_with_limit():
    clear_history_list()
    for i in range(5):
        time.sleep(0.01)
        client.post("/calculate", json={"expr": f"{i}+10"})

    get_result = client.get("/history", params={"limit": 2})
    assert get_result.status_code == 200
    data = get_result.json()
    print(data)
    assert len(data) == 2
    assert data[0]["expr"] == "4+10"
    assert data[1]["expr"] == "3+10"
    assert len(client.get("/history").json()) == 5
    assert len(client.get("/history", params={"limit": 99}).json()) == 5    #new assert lab03


def test_get_history_edge_cases():
    clear_history_list()
    empty_result = client.get("/history")
    assert empty_result.status_code == 200
    assert empty_result.json() == []
    client.post("/calculate", json={"expr": "7+7"})
    client.post("/calculate", json={"expr": "2**(3"})
    history_1 = client.get("/history").json()
    assert len(history_1) == 1
    history_limit_0 = client.get("/history", params={"limit": 0})
    assert len(history_limit_0.json()) == 1
    assert client.get("/history", params={"limit": "abc"}).status_code == 422
    assert history_1[0]["expr"] == "7+7"    #new assert lab03

# TEST CASE , delete history
def test_delete_history_clears_records():
    clear_history_list()
    client.post("/calculate", json={"expr": "5+5"})
    client.post("/calculate", json={"expr": "6+6"})
    assert len(client.get("/history").json()) == 2
    delete_result = client.delete("/history")
    assert delete_result.status_code == 200
    assert delete_result.json()["ok"] is True
    assert delete_result.json()["cleared"] is True
    assert client.get("/history").json() == []


def test_delete_history_when_already_empty():
    clear_history_list()
    assert client.get("/history").json() == []
    delete_result = client.delete("/history")
    assert delete_result.status_code == 200
    data = delete_result.json()
    assert data["ok"] is True
    assert data["cleared"] is True
    assert "error" not in data


def test_delete_history_then_record_again():
    clear_history_list()
    client.post("/calculate", json={"expr": "10*10"})
    assert client.delete("/history").json()["ok"] is True
    assert client.get("/history").json() == []
    client.post("/calculate", json={"expr": "20*20"})
    data = client.get("/history").json()
    assert len(data) == 1
    assert data[0]["expr"] == "20*20"
    assert data[0]["result"] == 400