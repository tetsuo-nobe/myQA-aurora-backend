-- myQA-rds 用テーブル作成 SQL
-- RDS PostgreSQL で実行してください
-- psql -h <RDS endpoint> -U postgres -d myqa -f sql/create_table.sql


-- 質問テーブル
CREATE TABLE IF NOT EXISTS questions (
    question_id   VARCHAR(36)  PRIMARY KEY,
    question_text TEXT         NOT NULL,
    questioner_name VARCHAR(100) NOT NULL,
    question_date TIMESTAMP    NOT NULL,
    category      VARCHAR(50)  NOT NULL DEFAULT '一般'
);

-- 回答テーブル（複合プライマリキー: question_id + answer_id）
CREATE TABLE IF NOT EXISTS answers (
    question_id   VARCHAR(36)  NOT NULL,
    answer_id     VARCHAR(4)   NOT NULL,
    answer_text   TEXT         NOT NULL,
    answerer_name VARCHAR(100) NOT NULL,
    answer_date   VARCHAR(30)  NOT NULL,
    PRIMARY KEY (question_id, answer_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
);
