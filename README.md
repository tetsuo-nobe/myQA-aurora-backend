# myQA-aurora-backend

Aurora Serverless v2 (PostgreSQL) を使用した Q&A アプリケーションのバックエンド API です。
AWS SAM でデプロイします。VPC、Aurora、Cognito User Pool はすべて SAM テンプレート内で作成されます。

## アーキテクチャ

- **Amazon API Gateway** (REST API) + Cognito User Pool オーソライザー
- **AWS Lambda** (Python 3.13) VPC 内配置
- **Amazon Aurora Serverless v2** (PostgreSQL 16.4)
- **Amazon Cognito User Pool** (Managed Login Page による認証)
- **VPC** (パブリック/プライベートサブネット、NAT Gateway)

### 認証フロー

Cognito Managed Login Page を使用した OAuth 2.0 認可コードフロー (PKCE) を採用しています。

1. フロントエンドが Cognito Managed Login Page にリダイレクト
2. ユーザーがログイン画面で認証
3. 認証成功後、認可コード付きでフロントエンドの `/callback` にリダイレクト
4. フロントエンドが認可コードを ID トークンに交換
5. API リクエスト時に ID トークンを `Authorization` ヘッダーに付与
6. API Gateway の Cognito Authorizer がトークンを検証

全 API エンドポイントで Cognito 認証が必須です。

## ディレクトリ構成

```
myQA-aurora-backend/
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
    └── create_tables.sql    # テーブル作成 SQL
```

## 前提条件

- AWS CLI がインストール・設定済みであること
- AWS SAM CLI がインストール済みであること
- Python 3.13 がインストール済みであること（sam build で使用）

## デプロイ手順

### 1. ビルド

```bash
sam build
```

### 2. デプロイ

```bash
sam deploy --guided
```

デプロイ時に指定するパラメータ:

| パラメータ | 説明 | デフォルト値 |
|-----------|------|-------------|
| DBName | データベース名 | myqa |
| DBUser | データベースマスターユーザー名 | postgres |
| DBPassword | データベースマスターパスワード（8文字以上） | なし（入力必須） |
| CognitoDomainPrefix | Cognito Managed Login Page のドメインプレフィックス（グローバルで一意） | なし（入力必須） |
| FrontendUrl | フロントエンドアプリケーションの URL | http://localhost:3000 |

2回目以降は `sam deploy` のみで OK です（`samconfig.toml` に設定が保存されます）。

### 3. テーブル作成

デプロイ後、`create-tables` Lambda 関数を実行してデータベースにテーブルを作成します:

```bash
aws lambda invoke --function-name myQA-aurora-backend-create-tables response.json
cat response.json
```

`"Tables created successfully."` と表示されれば成功です。

### 4. テスト用ユーザーの作成

Cognito User Pool はセルフサインアップが無効のため、管理者が AWS CLI でユーザーを作成します。

```bash
# ユーザー作成（username にメールアドレスを指定）
aws cognito-idp admin-create-user \
  --user-pool-id <UserPoolId> \
  --username user@example.com \
  --user-attributes Name=email_verified,Value=true \
  --temporary-password TempPass@1234

# パスワードを恒久的に設定（初回ログイン時のパスワード変更を省略する場合）
aws cognito-idp admin-set-user-password \
  --user-pool-id <UserPoolId> \
  --username user@example.com \
  --password YourPassword@1234 \
  --permanent
```

`<UserPoolId>` はデプロイ後の出力値（Outputs）から取得してください。

> **注意**: このユーザープールは `UsernameAttributes: email` で構成されているため、`--username` にメールアドレスを直接指定します。`--user-attributes` で `Name=email,Value=...` を指定する必要はありません（指定する場合は `--username` と同じ値にしてください）。

### 5. フロントエンドの環境変数設定

デプロイ後の出力値を使って、フロントエンド側の `.env.local` を設定します:

```
NEXT_PUBLIC_API_URL=<ApiUrl の値>
NEXT_PUBLIC_COGNITO_DOMAIN=<CognitoDomain の値>
NEXT_PUBLIC_COGNITO_CLIENT_ID=<UserPoolAppClientId の値>
NEXT_PUBLIC_REDIRECT_URI=http://localhost:3000/callback
NEXT_PUBLIC_LOGOUT_URI=http://localhost:3000
```

## デプロイ後の手順まとめ

```
1. sam build && sam deploy
2. aws lambda invoke で create-tables を実行（テーブル作成）
3. aws cognito-idp admin-create-user でユーザー作成
4. フロントエンドの .env.local に出力値を設定
5. フロントエンドを起動して動作確認
```

## API エンドポイント

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| GET | /questions | 質問一覧と回答数を取得 | Cognito |
| GET | /questions/{question_id} | 質問詳細と回答一覧を取得 | Cognito |
| POST | /questions | 質問を投稿 | Cognito |
| POST | /questions/{question_id}/answers | 回答を投稿 | Cognito |

## 出力値 (Outputs)

| キー | 説明 |
|------|------|
| ApiUrl | API Gateway エンドポイント URL |
| AuroraEndpoint | Aurora Serverless v2 エンドポイント |
| AuroraPort | Aurora Serverless v2 ポート |
| VPCId | VPC ID |
| UserPoolId | Cognito User Pool ID |
| UserPoolAppClientId | Cognito User Pool アプリクライアント ID |
| CognitoDomain | Cognito Managed Login Page URL |

## 注意事項

- `CognitoDomainPrefix` はグローバルで一意である必要があります。既に使用されている場合はデプロイが失敗します。
- NAT Gateway は時間課金が発生します。不要になったらスタックを削除してください。
- スタック削除: `aws cloudformation delete-stack --stack-name myQA-aurora-backend`
