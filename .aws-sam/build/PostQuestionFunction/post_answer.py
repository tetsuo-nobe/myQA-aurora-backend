"""
回答投稿 Lambda 関数
POST /questions/{question_id}/answers
指定された質問に対する回答を RDS PostgreSQL に保存する
"""
import json
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
    """回答を投稿して保存する"""
    conn = None
    try:
        question_id = event["pathParameters"]["question_id"]
        body = json.loads(event["body"])
        answer_text = body["answer_text"]
        answerer_name = body["answerer_name"]
        answer_date = datetime.now().strftime("%Y/%m/%d/%H:%M:%S")

        conn = get_connection()
        with conn.cursor() as cur:
            # 該当質問が存在するか確認
            cur.execute("SELECT question_id FROM questions WHERE question_id = %s", (question_id,))
            if not cur.fetchone():
                return {"statusCode": 404, "headers": HEADERS, "body": json.dumps({"error": "質問が見つかりません"}, ensure_ascii=False)}

            # 次の answer_id を連番で採番（0001形式）
            cur.execute("""
                SELECT COALESCE(MAX(CAST(answer_id AS INTEGER)), 0) + 1
                FROM answers
                WHERE question_id = %s
            """, (question_id,))
            next_id = cur.fetchone()[0]
            answer_id = str(next_id).zfill(4)

            cur.execute("""
                INSERT INTO answers (question_id, answer_id, answer_text, answerer_name, answer_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (question_id, answer_id, answer_text, answerer_name, answer_date))
        conn.commit()

        return {
            "statusCode": 201,
            "headers": HEADERS,
            "body": json.dumps({
                "question_id": question_id,
                "answer_id": answer_id,
                "answer_text": answer_text,
                "answerer_name": answerer_name,
                "answer_date": answer_date,
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
