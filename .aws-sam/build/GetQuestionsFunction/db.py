"""
データベース接続ユーティリティモジュール
RDS PostgreSQL への接続を管理する
"""
import os
import psycopg2
import psycopg2.extras


def get_connection():
    """RDS PostgreSQL への接続を取得する"""
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ.get("DB_PORT", "5432"),
    )
