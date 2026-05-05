import os
import re
import datetime

# 1. 環境変数からIssueデータを取得
title = os.getenv("ISSUE_TITLE", "No Title").strip()
body = os.getenv("ISSUE_BODY", "No Body").strip()

# ---------------------------------------------------------
# Step 1: タグの自動選別とファイル名生成
# ---------------------------------------------------------
# タイトルの先頭にある [TAG] を探す (例: "[GAME] 新しいUI案")
match = re.match(r"^\[([A-Za-z0-9_-]+)\]", title)
if match:
    tag = match.group(1).upper()
    clean_title = title[match.end():].strip()
else:
    tag = "IDEAS"
    clean_title = title

# OSでファイル名に使えない記号を削除・置換して安全な名前にする
safe_title = re.sub(r'[\\/*?:"<>|]', "", clean_title)
safe_title = safe_title.replace(" ", "_")

# タグごとに個別のフォルダを作成 (例: articles/GAME/)
tag_dir = f"articles/{tag}"
os.makedirs(tag_dir, exist_ok=True)
os.makedirs("contexts", exist_ok=True)

# ---------------------------------------------------------
# Step 2: 記事ファイル(個別)の作成
# ---------------------------------------------------------
# タイムスタンプを取得 (例: 20251125_143000)
now_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
# 個別記事のファイル名 (例: 20251125_143000_新しいUI案.md)
article_filename = f"{now_str}_{safe_title}.md"
article_path = os.path.join(tag_dir, article_filename)

# 記事のフォーマット
entry_block = f"# {clean_title}\n\n{body}\n"

with open(article_path, "w", encoding="utf-8") as f:
    f.write(entry_block)

# ---------------------------------------------------------
# Step 3: ペライチ文脈の更新（最新の複数ファイルから2000文字抽出）
# ---------------------------------------------------------
context_path = f"contexts/ctx_{tag}.md"
context_text = f"# CONTEXT: {tag}\n※最新の2000文字以内のみを保持しています。\n\n"
current_length = len(context_text)

# tag_dir(該当タグのフォルダ)内にある全 .md ファイルを取得し、名前で「降順（新しい順）」にソート
all_files = [f for f in os.listdir(tag_dir) if f.endswith(".md")]
all_files.sort(reverse=True)

recent_blocks = []
for file_name in all_files:
    file_path = os.path.join(tag_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
         content = f.read().strip()
    
    # 今回読み込んだファイルの文字数を判定
    if current_length + len(content) + 10 <= 2000:
        recent_blocks.append(content)
        current_length += len(content) + 10
    else:
        break # 2000文字を超えたら、それ以上古いファイルは切り捨てて読まない

# 時間軸を正常（上から古い順、下に最新）に戻して結合
recent_blocks.reverse()
final_context = context_text + "\n\n---\n\n".join(recent_blocks) + "\n\n---\n"

# 抽出したコンテキストで上書き保存
with open(context_path, "w", encoding="utf-8") as f:
    f.write(final_context)

print(f"✅ Success: Saved article '{article_filename}' and updated context for [{tag}].")
