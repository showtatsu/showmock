# 簡易モックサーバ (showmock)

ディレクトリにファイルを置いてモックにします。
ちょっとだけカスタマイズできます。

# 使い方

```sh
python -m showmock /app/data --content-type application/json
```

コンテナ版

```
docker run --rm -it -p 8000:8000 -v $(pwd)/data:/app/data ghcr.io/showtatsu/showmock:master /app/data
```


# 設定値

| 起動引数  | 環境変数    | default          | description                  |
| --------- | -------------------- | ---------------- | ---------------------------- |
| (１つ目の位置引数) | `DATA_DIR`    | ./data         | モックデータのルートディレクトリ |
| `--content-type application/json`  | `DEFAULT_CONTENT_TYPE` | `application/json` | デフォルトで応答するContent-Type |
| `--default-host default`  | `DEFAULT_HOSZT` | `default` | デフォルト(Hostヘッダに適合するモックフォルダが存在しない場合)のモックフォルダ |
| `--bind 0.0.0.0:8000` | `BIND`     | 0.0.0.0:8000   | gunicornサーバがListenするポート |

# ディレクトリ構造

`/app/data` (環境変数より変更可能) 以下のディレクトリにモックデータを格納します。

典型的なモックの置き場所はこのような位置になります。

`/app/data/example.com/get/api/sample`

- `/app/data`   : モックデータのルートディレクトリ
- `./example.com` : モックにアクセスを受けた際の`Host`ヘッダ値
- `./get`         : モックにアクセスを受けた際のHTTPメソッド(小文字)
- `./api/sample` : モックにアクセスを受けた際のHTTPパス (`/api/sample`に対応)

モックのデータはドメイン名のディレクトリに格納します。
ドメインディレクトリ自体は起動時に読み込まれますので、ドメインディレクトリの追加・削除の反映にはプロセスの再起動が必要です。

ドメインディレクトリ内部の構造は下記の通りです。

```
example.com
  |
  +--- _meta.yml ... モックに対して、ドメイン単位で個別の設定を指定します
  |
  +--- get  ... GETに応答するデータを格納します。(設定によってこの階層は省略されることがあります)
  |     |
  |     +--- api/
  |           +--- _index       ... /api または /api/ へのGETに対する応答データ
  |           +---example.json  ... /api/example.json へのGETに対する応答データ
  |
  +--- post  ... POSTに応答するデータを格納します。(設定によってこの階層は省略されることがあります)
  |     |
  |     +--- api/
  |           +--- _index       ... /api または /api/ へのPOSTに対する応答データ
  |           +---example.json  ... /api/example.json へのPOSTに対する応答データ
```

`_meta.yml` に `method_free: true` が指定されている場合、下記のようにメソッド名のディレクトリは省略されます。
この場合、いずれのメソッドに対しても同様の応答になります。

```
example.com
  |
  +--- _meta.yml ... モックに対して、ドメイン単位で個別の設定を指定します
  |
  +--- api/
        +--- _index       ... /api または /api/ へのアクセスに対する応答データ
        +---example.json  ... /api/example.json へのアクセスに対する応答データ
```


## 応答の content-type ヘッダ

応答に際して`Content-Type`ヘッダを生成する際、ソースとなるファイルの拡張子は意味をなしません。

`Content-Type`はモックに設定された情報とリクエストを元に、下記の優先度で決定されます。

1. _meta.yml の `headers` に `content-type` が指定されていれば、その値を応答します
2. リクエストに`required-content-type`ヘッダが指定されていれば、その値を応答します
3. リクエストのAcceptヘッダが下記のいずれかであれば、その値を応答します
  - application/json
  - application/xml
4. _meta.yml の トップレベル に `content-type` が指定されていれば、その値を応答します
5. DEFAULT_CONTENT_TYPE 環境変数に指定された値を応答します
6. `application/json`を応答します



# ドメインメタデータ

ドメインディレクトリ直下に、`_meta.yml`ファイルを作成することで
モックに対して追加の設定データを渡すことができます。

このファイルは起動時に読み込まれます。変更時はプロセスの再起動が必要です。

```yml
# headersは、辞書を指定します。
# このドメインのモックは、ここに指定されたヘッダを常に応答します。
headers:
  x-custom-header1: XXXXX
# method_freeは、boolean値です。デフォルトは false です。
# trueが指定されると、このドメインのモックのディレクトリ構造の中で
# HTTPメソッドを識別する階層が省略されます。
method_free: false
```
