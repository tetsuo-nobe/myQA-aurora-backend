#!/bin/bash
# Lambda レイヤー用の依存ライブラリをビルドするスクリプト
# このスクリプトを実行して python ディレクトリに psycopg2 をインストールする

set -e

echo "Lambda レイヤー用の依存ライブラリをインストールしています..."

# 既存の python ディレクトリを削除
rm -rf python

# psycopg2-binary をインストール
pip install -r requirements.txt -t python/

echo "ビルド完了: python/ ディレクトリに依存ライブラリがインストールされました"
