#!/bin/bash

# 文芸プラットフォーム エラー修正スクリプト v2
# Backref衝突エラーに対応

PROJECT_DIR="/home/bungeidaigaku/bungei-platform-complete"

echo "======================================"
echo "文芸プラットフォーム エラー修正 v2"
echo "======================================"
echo ""

# 1. comment.py の修正（Backref削除版）
echo "[1/4] comment.py の修正（Backref衝突を解消）..."
cat > "${PROJECT_DIR}/app/models/comment.py" << 'EOF'
from datetime import datetime
from app import db

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 引用コメント用フィールド
    quoted_text = db.Column(db.Text, nullable=True)
    quote_position = db.Column(db.Integer, nullable=True)
    
    # リレーションシップ（backrefなし - Userモデル側で定義されている）
    user = db.relationship('User', back_populates='comments')
    novel = db.relationship('Novel', back_populates='comments')
    
    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'
EOF
echo "✅ comment.py 修正完了"

# 2. novel.py のリレーションシップ修正
echo "[2/4] novel.py のリレーションシップ修正..."
cp "${PROJECT_DIR}/app/models/novel.py" "${PROJECT_DIR}/app/models/novel.py.backup"

python3 << 'PYTHON_EOF'
import re

novel_py_path = '/home/bungeidaigaku/bungei-platform-complete/app/models/novel.py'

with open(novel_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# commentsのリレーションシップをback_populatesに変更し、lazy='dynamic'を追加
# パターン1: backref='novel'がある場合
content = re.sub(
    r"comments\s*=\s*db\.relationship\(\s*['\"]Comment['\"]\s*,\s*backref\s*=\s*['\"]novel['\"]\s*\)",
    "comments = db.relationship('Comment', back_populates='novel', lazy='dynamic')",
    content
)

# パターン2: 既にback_populatesだがlazyがない場合
if "back_populates='novel'" in content and "lazy='dynamic'" not in content:
    content = re.sub(
        r"(comments\s*=\s*db\.relationship\([^)]+back_populates\s*=\s*['\"]novel['\"])",
        r"\1, lazy='dynamic'",
        content
    )

with open(novel_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Novel.py updated successfully")
PYTHON_EOF
echo "✅ novel.py 修正完了"

# 3. user.py のリレーションシップ確認・修正
echo "[3/4] user.py のリレーションシップ確認..."
python3 << 'PYTHON_EOF'
import re

user_py_path = '/home/bungeidaigaku/bungei-platform-complete/app/models/user.py'

try:
    with open(user_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # commentsリレーションシップが存在するか確認
    if 'comments' in content and 'relationship' in content:
        # backref形式をback_populatesに変更
        content = re.sub(
            r"comments\s*=\s*db\.relationship\(\s*['\"]Comment['\"]\s*,\s*backref\s*=\s*['\"]user['\"]\s*\)",
            "comments = db.relationship('Comment', back_populates='user', lazy='dynamic')",
            content
        )
        
        # lazy='dynamic'がない場合追加
        if "comments = db.relationship" in content and "lazy='dynamic'" not in content.split('comments = db.relationship')[1].split('\n')[0]:
            content = re.sub(
                r"(comments\s*=\s*db\.relationship\([^)]+)",
                r"\1, lazy='dynamic'",
                content,
                count=1
            )
        
        with open(user_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("User.py updated successfully")
    else:
        print("User.py: commentsリレーションシップが見つかりません（手動確認が必要）")
except FileNotFoundError:
    print("Warning: user.py not found")
PYTHON_EOF
echo "✅ user.py 確認完了"

# 4. base.html の無限ループ修正
echo "[4/4] base.html の無限ループ修正..."
cp "${PROJECT_DIR}/app/templates/base.html" "${PROJECT_DIR}/app/templates/base.html.backup" 2>/dev/null

python3 << 'PYTHON_EOF'
base_html_path = '/home/bungeidaigaku/bungei-platform-complete/app/templates/base.html'

try:
    with open(base_html_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 先頭の不正な行を削除
    cleaned_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        # 1-5行目にある不正な継承文を削除
        if i < 5 and ("content = '''{% extends" in line or "{% extends 'base.html'" in line):
            skip_next = True
            continue
        if skip_next and "'''" in line:
            skip_next = False
            continue
        if not skip_next:
            cleaned_lines.append(line)
    
    with open(base_html_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    print("base.html cleaned successfully")
except FileNotFoundError:
    print("Warning: base.html not found")
PYTHON_EOF
echo "✅ base.html 修正完了"

# 5. novels/list.html のコメント数表示修正
echo "[5/5] novels/list.html のコメント数修正..."
python3 << 'PYTHON_EOF'
import re

list_html_path = '/home/bungeidaigaku/bungei-platform-complete/app/templates/novels/list.html'

try:
    with open(list_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # パターン1: {{ novel.comments|length if novel.comments else 0 }}
    content = re.sub(
        r'\{\{\s*novel\.comments\|length\s+if\s+novel\.comments\s+else\s+0\s*\}\}',
        '{{ novel.comments.count() }}',
        content
    )
    
    # パターン2: {{ novel.comments|length }}
    content = re.sub(
        r'\{\{\s*novel\.comments\|length\s*\}\}',
        '{{ novel.comments.count() }}',
        content
    )
    
    with open(list_html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("novels/list.html updated successfully")
except FileNotFoundError:
    print("Warning: novels/list.html not found")
PYTHON_EOF
echo "✅ novels/list.html 修正完了"

echo ""
echo "======================================"
echo "🎉 すべての修正が完了しました！"
echo "======================================"
echo ""
echo "次のステップ:"
echo "1. PythonAnywhereのWebタブで「Reload」ボタンをクリック"
echo "2. サイトにアクセスして動作確認"
echo ""
echo "バックアップファイル:"
echo "- ${PROJECT_DIR}/app/models/novel.py.backup"
echo "- ${PROJECT_DIR}/app/templates/base.html.backup"
echo ""
