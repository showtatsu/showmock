from typing import Optional
from fastapi import Response
import os
import yaml
import logging


SUPPORTED_ACCEPT_HEADERS = [x.lower() for x in [
    'application/json',
    'application/xml',
]]


class MockDomain():
    """ モックドメイン： 1ドメイン分のモデル。

    Raises:
        ValueError: 渡されたパスがディレクトリでない場合
    """

    index_file = '_index'
    meta_file = '_meta.yml'

    def __init__(self,
                 domain_dir: str,
                 default_content_type: str = 'application/json',
                 supported_accept_headers: Optional[list[str]] = SUPPORTED_ACCEPT_HEADERS,
                 empty: bool = False,
                 ) -> None:
        """ コンストラクタ。モックデータを格納したディレクトリを渡してモックモデルを作成します。

        Args:
            domain_dir (str): モックデータを格納したディレクトリを渡す。
        """
        self.domain_dir = domain_dir
        self.domain = os.path.basename(domain_dir)
        self.meta = self.__class__.Meta(os.path.join(domain_dir, self.__class__.meta_file))
        self.default_content_type = default_content_type
        self.supported_accept_headers = supported_accept_headers
        self.empty = empty
        self.logger = logging.getLogger("showmock")

    class Meta():
        """ メタクラス
        """

        def __init__(self, metafile) -> None:
            if os.path.isfile(metafile):
                with open(metafile, 'r') as reader:
                    meta = yaml.load(reader, yaml.loader.SafeLoader)
                self._meta = meta
            else:
                self._meta = {}

        @property
        def headers(self):
            """ このモックから常時応答するHTTPヘッダリスト
            """
            if self._meta is None:
                return {}
            headers = self._meta.get('headers')
            if headers and isinstance(headers, dict):
                return headers

        @property
        def content_type(self):
            if self._meta is not None:
                return self._meta.get('content-type')

        @property
        def method_free(self):
            """ このモックがHTTPメソッドを識別してサブディレクトリから
            ファイルを検索するかどうかを確認します。
            """
            if self._meta is None:
                return False
            return self._meta.get("method_free")

    @classmethod
    def list_mock_domains(cls, datadir: str) -> list["MockDomain"]:
        """ ディレクトリの下にあるモックドメインディレクトリを参照してMockDomainクラスのオブジェクトを返します。
        """
        if not os.path.isdir(datadir):
            raise ValueError("data path is not a directory.")
        directories = [os.path.join(datadir, x) for x in os.listdir(datadir)]
        mock_domains = [cls(d) for d in directories if os.path.isdir(d)]
        return mock_domains

    @classmethod
    def create_empty_mock(cls):
        """ 空っぽのモックを作成します
        """
        return cls(domain_dir='/dev/null', empty=True)

    def get_response(self, method: str, path: str, accept: str, params: Optional[dict] = dict()) -> Response:
        """ リクエストの情報を元に、モックモデルからコンテンツを読み出します。

        Args:
            method (str): HTTPメソッド
            path (str): HTTPリクエストパス
            accept (str): HTTP Acceptヘッダ
            params (Optional[dict], optional): パラメータ

        Returns:
            Response: FastAPI Responseオブジェクト
        """
        # FastAPIが"/"を基準に正規化してくれるけど見た目怖く見えるので一応
        path = self.normalize_path(path=path)
        if self.meta.method_free:
            filepath = os.path.join(self.domain_dir, path)
        else:
            filepath = os.path.join(self.domain_dir, method, path)

        headers = self.meta.headers
        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, self.__class__.index_file)
        media = self.get_media_type(accept)

        self.logger.debug(f"Search: {method} {self.domain}/{path} -> {filepath}")

        # Empty mock
        if self.empty:
            response = Response(content=None, status_code=404, media_type=media, headers=headers)
        # Not found
        elif not os.path.isfile(filepath):
            response = Response(content=None, status_code=404, media_type=media, headers=headers)
        # Contents
        else:
            with open(filepath, 'rb') as reader:
                content = reader.read()
                reader.close()
            response = Response(content=content, status_code=200, media_type=media, headers=headers)
        return response

    def get_media_type(self, accept: str) -> str:
        """ 応答するContent-Typeヘッダを生成します。

        Args:
            accept (str): Acceptヘッダの値

        Returns:
            str: Content-Typeに付与すべき文字列
        """
        if accept in self.supported_accept_headers:
            media = accept
        elif self.meta.content_type:
            media = self.meta.content_type
        else:
            media = self.default_content_type
        return media

    def normalize_path(self, path: str) -> str:
        s = os.path.join('/', path)
        s = os.path.normpath(s)
        s = s.lstrip('/')
        return s
