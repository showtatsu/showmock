import dotenv
from .cli import start_server


if __name__ == '__main__':
    dotenv.load_dotenv()
    start_server()
