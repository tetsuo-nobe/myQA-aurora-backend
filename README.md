# myQA-aurora-backend

* 課題: Q&amp;A アプリケーションのバックエンド (Aurora Serverless 使用）

Aurora Serverless v2 (PostgreSQL) を使用した Q&A アプリケーションのバックエンド API です。
AWS SAM でデプロイします。VPC、Aurora、Cognito User Pool はすべて SAM テンプレート内で作成されます。

## アーキテクチャ

- Amazon API Gateway (REST API) + Cognito User Pool オーソライザー
- AWS Lambda (Python 3.13) VPC 内配置
- Amazon Aurora Serverless v2 (PostgreSQL 16.4、Data API 有効)
- Amazon Cognito User Pool
- VPC (パブリック/プライベートサブネット、NAT Gateway)

## ディレクトリ構成

```
myQA-rds/
├── template.yaml            # SAM テンプレート
├── samconfig.toml           # SAM CLI 設定
├── src/                     # Lambda 関数ソース
│   ├── db.py                # DB 接続ユーティリティ
│   ├── get_questions.py     # GET /questions
│   ├── get_question.py      # GET /questions/{question_id}
│   ├── post_question.py     # POST /questions
│   ├── post_answer.py       # POST /questions/{question_id}/answers
│   └── create_tables.py     # テーブル作成（API Gateway 統合なし）
├── layers/deps/             # Lambda レイヤー (psycopg2)
│   └── requirements.txt
└── sql/
    ├── create_tables.sql    # テーブル作成 SQL
    └── create_table.sql     # テーブル作成 SQL（別版）
```

## 前提条件

- AWS CLI および SAM CLI がインストール済みであること
- Python 3.13 がインストール済みであること（sam build で使用）

## デプロイ

```bash
cd myQA-rds
sam build
sam deploy --guided
```

デプロイ時に指定するパラメータ:
- DBName: データベース名（デフォルト: myqa）
- DBUser: データベースマスターユーザー名（デフォルト: postgres）
- DBPassword: データベースマスターパスワード（8文字以上）

VPC、Aurora Serverless v2、Cognito User Pool は SAM テンプレートにより自動作成されます。

## テーブル作成

デプロイ後、CreateTables Lambda 関数を実行してテーブルを作成します:

```bash
aws lambda invoke --function-name myQA-rds-create-tables output.json
```

## API エンドポイント

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| GET | /questions | 質問一覧と回答数を取得 | なし |
| GET | /questions/{question_id} | 質問詳細と回答一覧を取得 | なし |
| POST | /questions | 質問を投稿 | なし |
| POST | /questions/{question_id}/answers | 回答を投稿 | なし |

## 出力値

| キー | 説明 |
|------|------|
| ApiUrl | API Gateway エンドポイント URL |
| AuroraEndpoint | Aurora Serverless v2 エンドポイント |
| AuroraPort | Aurora Serverless v2 ポート |
| VPCId | VPC ID |
| UserPoolId | Cognito User Pool ID |
| UserPoolAppClientId | Cognito User Pool アプリクライアント ID |

