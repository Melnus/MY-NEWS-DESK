import os
import re

# 1. 環境変数からIssueデータを取得
title = os.getenv("ISSUE_TITLE", "No Title").strip()
body = os.getenv("ISSUE_BODY", "No Body").strip()

# フォルダ作成
os.makedirs("articles", exist_ok=True)
os.makedirs("contexts", exist_ok=True)

# ---------------------------------------------------------
# Step 1: タグの自動選別（AI不要の正規表現マッチング）
# ---------------------------------------------------------
# タイトルの先頭にある [TAG] を探す (例: "[GAME] 新しいUI案")
match = re.match(r"^\[([A-Za-z0-9_-]+)\]", title)
if match:
    tag = match.group(1).upper()
    clean_title = title[match.end():].strip() # タイトルからタグを取り除く
else:
    tag = "IDEAS" # タグがなければ IDEAS フォルダへ
    clean_title = title

# ---------------------------------------------------------
# Step 2: 記事ログ(無制限)への追記
# ---------------------------------------------------------
article_path = f"articles/{tag}.md"
entry_block = f"## {clean_title}\n{body}\n\n---\n"

with open(article_path, "a", encoding="utf-8") as f:
    f.write(entry_block)

# ---------------------------------------------------------
# Step 3: ペライチ文脈の更新（最新から2000文字スクリーニング）
# ---------------------------------------------------------
# articlesの全内容を読み込み、ブロックごとに分割
with open(article_path, "r", encoding="utf-8") as f:
    content = f.read()

# '---' で区切ってリスト化し、空の要素を消す
blocks = [b.strip() for b in content.split("---") if b.strip()]

context_path = f"contexts/ctx_{tag}.md"
context_text = f"# CONTEXT: {tag}\n※最新の2000文字以内のみを保持しています。\n\n"
current_length = len(context_text)

# 新しい（後ろにある）ブロックから順番に足していく
recent_blocks = []
for block in reversed(blocks):
    if current_length + len(block) + 10 <= 2000:
        recent_blocks.append(block)
        current_length += len(block) + 10
    else:
        break # 2000文字を超えたらそれ以上古い情報は捨てる

# 時間軸を正常（上から古い順、下に最新）に戻して結合
recent_blocks.reverse()
final_context = context_text + "\n\n---\n\n".join(recent_blocks) + "\n\n---\n"

with open(context_path, "w", encoding="utf-8") as f:
    f.write(final_context)

print(f"✅ Success: Processed under tag [{tag}].")
