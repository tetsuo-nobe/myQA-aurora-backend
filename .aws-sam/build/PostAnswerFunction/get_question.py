"""
質問詳細＋回答一覧取得 Lambda 関数
GET /questions/{question_id}
指定された質問の詳細と、その質問に対する全回答を返す
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
    """質問詳細と回答一覧を取得して返す"""
    conn = None
    try:
        question_id = event["pathParameters"]["question_id"]
        conn = get_connection()
        with conn.cursor() as cur:
            # 質問の詳細を取得
            cur.execute("""
                SELECT question_id, question_text, questioner_name,
                       TO_CHAR(question_date, 'YYYY/MM/DD/HH24:MI:SS') AS question_date,
                       category
                FROM questions
                WHERE question_id = %s
            """, (question_id,))
            q_row = cur.fetchone()
            if not q_row:
                return {"statusCode": 404, "headers": HEADERS, "body": json.dumps({"error": "質問が見つかりません"}, ensure_ascii=False)}

            question = {
                "question_id": q_row[0],
                "question_text": q_row[1],
                "questioner_name": q_row[2],
                "question_date": q_row[3],
                "category": q_row[4],
            }

            # 回答一覧を取得
            cur.execute("""
                SELECT answer_id, answer_text, answerer_name, answer_date
                FROM answers
                WHERE question_id = %s
                ORDER BY answer_id ASC
            """, (question_id,))
            a_rows = cur.fetchall()
            answers = []
            for row in a_rows:
                answers.append({
                    "answer_id": row[0],
                    "answer_text": row[1],
                    "answerer_name": row[2],
                    "answer_date": row[3],
                })

            question["answers"] = answers

        return {"statusCode": 200, "headers": HEADERS, "body": json.dumps(question, ensure_ascii=False)}
    except Exception as e:
        print(f"エラー発生: {e}")
        return {"statusCode": 500, "headers": HEADERS, "body": json.dumps({"error": str(e)}, ensure_ascii=False)}
    finally:
        if conn:
            conn.close()
