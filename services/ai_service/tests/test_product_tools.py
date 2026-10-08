import asyncio

from app.tools.product_tools import ProductServiceClient


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class RecordingClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def test_search_products_uses_public_catalog_search_endpoint(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"items": [{"id": 1, "name": "Organic Apples"}]}))
    monkeypatch.setattr("app.tools.product_tools.httpx.AsyncClient", lambda **kwargs: transport)
    client = ProductServiceClient(base_url="http://product-service")

    result = asyncio.run(client.search_products("apples"))

    assert result == {"success": True, "products": [{"id": 1, "name": "Organic Apples"}]}
    assert transport.calls == [("http://product-service/api/v1/products/", {"params": {"search": "apples"}})]


def test_get_product_uses_public_catalog_detail_endpoint(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"id": 7, "name": "Organic Lime"}))
    monkeypatch.setattr("app.tools.product_tools.httpx.AsyncClient", lambda **kwargs: transport)
    client = ProductServiceClient(base_url="http://product-service")

    result = asyncio.run(client.get_product(7))

    assert result == {"success": True, "product": {"id": 7, "name": "Organic Lime"}}
    assert transport.calls == [("http://product-service/api/v1/products/7", {})]


def test_search_products_rejects_malformed_catalog_response(monkeypatch):
    transport = RecordingClient(FakeResponse(200, {"unexpected": "response"}))
    monkeypatch.setattr("app.tools.product_tools.httpx.AsyncClient", lambda **kwargs: transport)

    result = asyncio.run(ProductServiceClient().search_products("apples"))

    assert result["success"] is False
    assert result["error"] == "invalid_response"
