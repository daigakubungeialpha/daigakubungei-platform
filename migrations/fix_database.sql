-- commentsテーブルのカラム名を修正
-- SQLiteでは直接カラム名変更ができないため、テーブルを再作成

-- 一時テーブル作成
CREATE TABLE comments_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    quoted_text TEXT,
    quote_position INTEGER,
    novel_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (novel_id) REFERENCES novels(id),
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- データコピー（user_idカラムがある場合）
INSERT INTO comments_new (id, content, quoted_text, quote_position, novel_id, author_id, created_at)
SELECT id, content, quoted_text, quote_position, novel_id, 
       COALESCE(user_id, author_id, 1), created_at
FROM comments;

-- 古いテーブル削除
DROP TABLE comments;

-- 新しいテーブルをリネーム
ALTER TABLE comments_new RENAME TO comments;

-- インデックス再作成
CREATE INDEX ix_comments_created_at ON comments(created_at);
