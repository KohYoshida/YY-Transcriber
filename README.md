# Audio Transcription App

This application is a web application created using Flask, designed to convert audio files into text. The function to convert to text utilizes OpenAI's Whisper. Whisper has both a free open-source version and a paid API version, but this tool uses the API version. As of June 1, 2023, the cost is $0.006 per minute of audio data. For more details, please see [here](https://openai.com/pricing).

## Main Features

1. Language selection: The application supports both Japanese and English.

2. File upload: Users can upload audio files and have their contents converted into text.

3. Audio transcription: The application transcribes the uploaded audio files into text.

4. Display of results: The results of the conversion are displayed on the website.

5. Authentication: The application uses HTTP authentication.

## Installation and Setup

1. Clone this repository.

2. Run `pip install -r requirements.txt` to install the required packages.

3. Create a config.py file using config_TEMPLATE.py as a reference, and set the username and password (this username and password will be used for accessing the app).You will need API keys for OpenAI. More information on how to get API keys can be found [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key).

4. To run the application, execute `python app.py`.

## Contributions

Contributions to this project are most welcome. Feel free to participate in any form, whether it be bug reports, feature suggestions, or pull requests.

## License

This project is published under the MIT license. For more information, please [click here](https://mit-license.org/).


ーーーーーーー


# オーディオトランスクリプションアプリ

このアプリケーションは、Flaskを用いて制作された、オーディオファイルをテキストに変換するためのWebアプリケーションです。テキストに変換する機能はOpenAIのWhisperを活用しています。Whisperには無料のオープンソース版と有料のAPI版がありますが、このツールはAPI版を使用しています。2023年6月1日現在、費用はオーディオデータ1分あたり0.006米ドルです。詳しくは[こちら](https://openai.com/pricing)をご覧ください。

## 主な機能

1. 言語選択: アプリケーションは日本語と英語をサポートしています。

2. ファイルのアップロード: ユーザーはオーディオファイルをアップロードして、その内容をテキストに変換することができます。

3. オーディオのトランスクリプション: アプリケーションはアップロードされたオーディオファイルをテキストに変換します。

4. 結果の表示: 変換結果は、ウェブサイト上で表示されます。

5. 認証: アプリケーションはHTTP認証を使用します。

## インストールとセットアップ

1. このリポジトリをクローンします。

2. `pip install -r requirements.txt` を実行して必要なパッケージをインストールします。

3. config_TEMPLATE.pyを参考にconfig.pyファイルを作成し、ユーザー名とパスワードを設定します（このユーザー名とパスワードは、アプリへのアクセスに使用されます）。OpenAIのAPI keyの取得方法は[こちら](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)をご参照ください。

4. アプリケーションを実行するために、`python app.py`を実行します。

## 貢献

このプロジェクトへの貢献は大歓迎です。バグ報告、機能提案、プルリクエストなど、どんな形でもお気軽にご参加ください。

## ライセンス

このプロジェクトはMITライセンスのもとに公開されています。詳細は[こちら](https://licenses.opensource.jp/MIT/MIT.html)をご覧ください。
