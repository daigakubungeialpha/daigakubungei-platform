#!/usr/bin/env python3
"""データベースマイグレーションスクリプト"""

import sqlite3
import os
from datetime import datetime

def backup_database(db_path):
    """データベースのバックアップを作成"""
    if not os.path.exists(db_path):
        print(f"データベースが見つかりません: {db_path}")
        return None
    
    backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"バックアップ作成: {backup_path}")
    return backup_path

def migrate_comments_table(db_path):
    """commentsテーブルをマイグレーション"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 既存テーブルの構造確認
        cursor.execute("PRAGMA table_info(comments)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        print("現在のcommentsテーブル構造:")
        for col_name in columns:
            print(f"  - {col_name}")
        
        # user_idカラムが存在し、author_idが存在しない場合のみマイグレーション
        if 'user_id' in columns and 'author_id' not in columns:
            print("\nマイグレーション実行中...")
            
            # 一時テーブル作成
            cursor.execute("""
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
                )
            """)
            
            # データコピー
            cursor.execute("""
                INSERT INTO comments_new 
                (id, content, quoted_text, quote_position, novel_id, author_id, created_at)
                SELECT id, content, quoted_text, 
                       COALESCE(text_position, quote_position), 
                       novel_id, user_id, created_at
                FROM comments
            """)
            
            # 古いテーブル削除
            cursor.execute("DROP TABLE comments")
            
            # 新テーブルをリネーム
            cursor.execute("ALTER TABLE comments_new RENAME TO comments")
            
            # インデックス作成
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_comments_created_at ON comments(created_at)")
            
            conn.commit()
            print("✓ マイグレーション完了")
            
        elif 'author_id' in columns:
            print("\n既にauthor_idカラムが存在します。マイグレーション不要。")
        else:
            print("\n警告: 予期しないテーブル構造です。")
            
    except Exception as e:
        print(f"エラー: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    """メイン処理"""
    # データベースパスの候補
    db_paths = [
        'instance/bungei.db',
        'bungei.db',
        '../instance/bungei.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("データベースファイルが見つかりません。")
        print("新規データベースの場合、モデル定義から自動作成されます。")
        return
    
    print(f"データベース: {db_path}")
    
    # バックアップ作成
    backup_path = backup_database(db_path)
    
    if backup_path:
        # マイグレーション実行
        migrate_comments_table(db_path)
        print(f"\n完了! バックアップ: {backup_path}")

if __name__ == '__main__':
    main()
