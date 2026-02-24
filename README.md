# 文芸プラットフォーム - 完全版

## 🎨 概要

大学文芸サークル向けの洗練された小説投稿・合評プラットフォーム。
**「文芸誌のような美しい読書体験」**と**「noteやMediumのような洗練されたUI」**を実現。

## ✨ 主な機能

### 読者・作家向け
- ✅ モダンでミニマルなUI
- ✅ ドラッグ範囲選択コメント（校閲スタイル）
- ✅ 字体カスタマイズ（明朝・ゴシック・等幅）
- ✅ カテゴリー分類（創作/評論）
- ✅ いいね機能
- ✅ マイページ（タブ切り替え式）
- ✅ 作品検索・フィルター

### システム
- ✅ 会員登録・ログイン
- ✅ 管理者ダッシュボード
- ✅ レスポンシブデザイン

## 🚀 クイックスタート

### 1. 環境準備
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. データベース初期化
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. 管理者アカウント作成
```bash
flask create-admin
# ユーザー名: admin
# メール: admin@example.com
# パスワード: (任意)
```

### 4. 起動
```bash
python run.py
```

ブラウザで `http://localhost:5000` にアクセス！

## 📁 プロジェクト構造

```
bungei-platform/
├── app/
│   ├── __init__.py         # アプリ初期化
│   ├── models/             # データベースモデル
│   │   ├── user.py        # ユーザー
│   │   ├── novel.py       # 小説
│   │   ├── comment.py     # コメント
│   │   └── like.py        # いいね
│   ├── routes/             # ルーティング
│   │   ├── main.py        # トップページ
│   │   ├── auth.py        # 認証
│   │   ├── novels.py      # 小説機能
│   │   ├── comments.py    # コメント機能
│   │   ├── users.py       # プロフィール
│   │   └── admin.py       # 管理者
│   └── templates/          # HTMLテンプレート
│       ├── base.html      # ベース
│       ├── index.html     # トップ
│       ├── novels/        # 作品関連
│       ├── auth/          # 認証
│       ├── users/         # ユーザー
│       └── admin/         # 管理画面
├── config.py               # 設定
├── requirements.txt        # 依存パッケージ
└── run.py                  # 起動スクリプト
```

## 🎨 デザインの特徴

- **カラー**: モノトーンベースの上品な配色
- **フォント**: Google Fonts (Noto Serif/Sans JP)
- **レイアウト**: ミニマリズム、ゆったりとした余白
- **アニメーション**: 滑らかなホバー・トランジション

## 🔧 カスタマイズ例

### 字体追加
`app/models/novel.py`:
```python
def get_font_class(self):
    font_map = {
        'mincho': 'font-mincho',
        'gothic': 'font-gothic',
        'mono': 'font-mono',
        'custom': 'font-custom'  # 追加
    }
```

### カテゴリー追加
`templates/novels/create.html`:
```html
<option value="poetry">詩</option>
<option value="drama">戯曲</option>
```

## 📚 技術スタック

- **Backend**: Flask 3.0
- **Database**: SQLite (開発) / PostgreSQL (本番)
- **ORM**: SQLAlchemy
- **認証**: Flask-Login
- **Frontend**: Jinja2 + Vanilla JavaScript

## 🐛 トラブルシューティング

**データベースエラー:**
```bash
rm bungei.db
flask db upgrade
```

**ポート使用中:**
```bash
# run.py を編集
app.run(port=5001)
```

## 📖 さらに詳しく

- セットアップガイド: `docs/SETUP.md`
- 機能説明: `docs/FEATURES.md`

## 📄 ライセンス

大学文芸サークル内部利用専用

---

Happy Writing! ✨📚
