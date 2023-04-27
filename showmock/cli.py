import click
import dotenv
import uvicorn
import logging
import sys
from .server import create_app
from .customlogging import CustomFormatter


@click.command()
@click.option("-b", "--bind", envvar="BIND", default='0.0.0.0:8000')
@click.option("-c", "--content-type", envvar="DEFAULT_CONTENT_TYPE", default='application/json')
@click.option("-d", "--default-host", envvar="DEFAULT_HOST", default='default')
@click.option("-a", "--accept", multiple=True, envvar="ACCEPT_CONTENT_TYPES", default=['application/json', 'application/xml'])
@click.option('-r', '--required-content-type-header', envvar='REQUIRED_CONTENT_TYPE_HEADER', default='required-content-type')
@click.argument("data", envvar="DATA_DIR", default="data")
def start_server(data: str,
                 bind: str,
                 content_type: str,
                 default_host: str,
                 accept: list[str],
                 required_content_type_header: str,
                 ):
    """ モックサーバを起動します。
    """
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(CustomFormatter())

    log = logging.getLogger("showmock")
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)

    app = create_app(data_dir=data,
                     default_content_type=content_type,
                     default_host=default_host,
                     supported_accept_headers=accept,
                     required_content_type_header=required_content_type_header)
    host, port = bind.split(':')
    port = int(port)

    uvicorn.run(app=app, host=host, port=port)


if __name__ == '__main__':
    dotenv.load_dotenv()
    start_server()
