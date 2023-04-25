from fastapi import FastAPI, Header, Response
import os
import logging
from .mockdomain import MockDomain


# === 定数定義 ===============================

SUPPORTED_ACCEPT_HEADERS = [x.lower() for x in [
    'application/json',
    'application/xml',
]]


# === 処理部 ===============================

def create_app(data_dir: str = "data",
               default_content_type: str = "application/json",
               default_host: str = "default",
               supported_accept_headers: list[str] = SUPPORTED_ACCEPT_HEADERS,
               ) -> FastAPI:

    log = logging.getLogger("showmock")

    # モックモデルを読み込みます。
    if not os.path.isdir(data_dir):
        raise ValueError("data path is not a directory.")

    log.info(f"Lookup data in {data_dir} ...")
    directories = [os.path.join(data_dir, x) for x in os.listdir(data_dir)]
    options = dict(default_content_type=default_content_type, supported_accept_headers=supported_accept_headers)
    mock_domains = [MockDomain(domain_dir=d, **options) for d in directories if os.path.isdir(d)]
    mock_servers = {d.domain: d for d in mock_domains}

    for i, k in enumerate(mock_servers.keys()):
        log.info(f"[{i}] Mock domain loaded: {k}")

    if default_host and mock_servers.get(default_host):
        default_mock = mock_servers[default_host]
        log.info(f"Mock default is {default_host}")
    else:
        default_mock = MockDomain.create_empty_mock()
        log.info("Mock default is empty domain")

    # FastAPI オブジェクトの定義とハンドラの追加
    app = FastAPI()

    def serve(method: str, path: str, host: str = Header(), accept: str = Header()) -> Response:
        mock = mock_servers.get(host)
        if mock is None:
            mock = default_mock
        return mock.get_response(method, path=path, accept=accept, params={})

    @app.get('/{path:path}')
    async def serve_get(path: str, host: str = Header(), accept: str = Header()) -> Response:
        return serve(method="get", path=path, host=host, accept=accept)

    @app.post('/{path:path}')
    async def serve_post(path: str, host: str = Header(), accept: str = Header()) -> Response:
        return serve(method="post", path=path, host=host, accept=accept)

    @app.put('/{path:path}')
    async def serve_put(path: str, host: str = Header(), accept: str = Header()) -> Response:
        return serve(method="put", path=path, host=host, accept=accept)

    @app.delete('/{path:path}')
    async def serve_delete(path: str, host: str = Header(), accept: str = Header()) -> Response:
        return serve(method="delete", path=path, host=host, accept=accept)

    @app.patch('/{path:path}')
    async def serve_patch(path: str, host: str = Header(), accept: str = Header()) -> Response:
        return serve(method="patch", path=path, host=host, accept=accept)

    return app
