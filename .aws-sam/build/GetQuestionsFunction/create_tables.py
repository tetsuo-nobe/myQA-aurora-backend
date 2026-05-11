"""
Create tables Lambda function
Creates questions and answers tables in RDS PostgreSQL.
This function is not integrated with API Gateway.
Invoke manually via AWS Console or CLI.
"""
from db import get_connection

# SQL for creating tables
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS questions (
    question_id     VARCHAR(36)   PRIMARY KEY,
    question_text   TEXT          NOT NULL,
    questioner_name VARCHAR(100)  NOT NULL,
    question_date   TIMESTAMP     NOT NULL,
    category        VARCHAR(50)   NOT NULL DEFAULT 'general'
);

CREATE TABLE IF NOT EXISTS answers (
    question_id   VARCHAR(36)   NOT NULL,
    answer_id     VARCHAR(4)    NOT NULL,
    answer_text   TEXT          NOT NULL,
    answerer_name VARCHAR(100)  NOT NULL,
    answer_date   VARCHAR(30)   NOT NULL,
    PRIMARY KEY (question_id, answer_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
);
"""


def lambda_handler(event, context):
    """Create tables in RDS PostgreSQL"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES_SQL)
        conn.commit()
        return {"statusCode": 200, "message": "Tables created successfully."}
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
        return {"statusCode": 500, "message": str(e)}
    finally:
        if conn:
            conn.close()
