"""
質問一覧取得 Lambda 関数
GET /questions
全ての質問と各質問の回答数を返す
"""
import json
from db import get_connection

# レスポンスヘッダー（CORS対応）
HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


def lambda_handler(event, context):
    """質問一覧と回答数を取得して返す"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # 質問一覧と各質問の回答数を取得するクエリ
            cur.execute("""
                SELECT
                    q.question_id,
                    q.question_text,
                    q.questioner_name,
                    TO_CHAR(q.question_date, 'YYYY/MM/DD/HH24:MI:SS') AS question_date,
                    q.category,
                    COUNT(a.answer_id) AS answer_count
                FROM questions q
                LEFT JOIN answers a ON q.question_id = a.question_id
                GROUP BY q.question_id, q.question_text, q.questioner_name, q.question_date, q.category
                ORDER BY q.question_date DESC
            """)
            rows = cur.fetchall()
            # 結果をリスト形式に変換
            questions = []
            for row in rows:
                questions.append({
                    "question_id": row[0],
                    "question_text": row[1],
                    "questioner_name": row[2],
                    "question_date": row[3],
                    "category": row[4],
                    "answer_count": row[5],
                })
        return {"statusCode": 200, "headers": HEADERS, "body": json.dumps(questions, ensure_ascii=False)}
    except Exception as e:
        print(f"エラー発生: {e}")
        return {"statusCode": 500, "headers": HEADERS, "body": json.dumps({"error": str(e)}, ensure_ascii=False)}
    finally:
        if conn:
            conn.close()
