import requests

BASE_URL = "http://127.0.0.1:8000"


def api_request(method, endpoint, data=None):

    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            json=data,
            timeout=20
        )

        response.raise_for_status()

        if not response.content:
            return {"status": "success"}

        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": str(e)
        }


def get_request(endpoint):
    return api_request("GET", endpoint)


def post_request(endpoint, data):
    return api_request("POST", endpoint, data)


def put_request(endpoint, data):
    return api_request("PUT", endpoint, data)


def delete_request(endpoint):
    return api_request("DELETE", endpoint)
