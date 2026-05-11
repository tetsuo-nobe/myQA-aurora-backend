"""
質問投稿 Lambda 関数
POST /questions
新しい質問を RDS PostgreSQL に保存する
"""
import json
import uuid
from datetime import datetime
from db import get_connection

# レスポンスヘッダー（CORS対応）
HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


def lambda_handler(event, context):
    """質問を投稿して保存する"""
    conn = None
    try:
        body = json.loads(event["body"])
        question_id = str(uuid.uuid4())
        question_text = body["question_text"]
        questioner_name = body["questioner_name"]
        category = body.get("category", "一般")
        question_date = datetime.now()

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO questions (question_id, question_text, questioner_name, question_date, category)
                VALUES (%s, %s, %s, %s, %s)
            """, (question_id, question_text, questioner_name, question_date, category))
        conn.commit()

        return {
            "statusCode": 201,
            "headers": HEADERS,
            "body": json.dumps({
                "question_id": question_id,
                "question_text": question_text,
                "questioner_name": questioner_name,
                "question_date": question_date.strftime("%Y/%m/%d/%H:%M:%S"),
                "category": category,
            }, ensure_ascii=False),
        }
    except Exception as e:
        print(f"エラー発生: {e}")
        if conn:
            conn.rollback()
        return {"statusCode": 500, "headers": HEADERS, "body": json.dumps({"error": str(e)}, ensure_ascii=False)}
    finally:
        if conn:
            conn.close()
