import os
import re
import datetime

# 1. データの取得
title_raw = os.getenv("ISSUE_TITLE", "No Title").strip()
body = os.getenv("ISSUE_BODY", "No Body").strip()

# フォルダ作成
os.makedirs("contexts", exist_ok=True)

# --- Step 1: タグ選別 ---
match = re.match(r"^\[([A-Za-z0-9_-]+)\]", title_raw)
tag = match.group(1).upper() if match else "IDEAS"
clean_title = title_raw[match.end():].strip() if match else title_raw

tag_dir = f"articles/{tag}"
os.makedirs(tag_dir, exist_ok=True)

# --- Step 2: 記事保存（生ログ） ---
now_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
safe_file_title = re.sub(r'[\\/*?:"<>|]', '', clean_title).replace(' ', '_')
article_filename = f"{now_str}_{safe_file_title}.md"
article_path = os.path.join(tag_dir, article_filename)

with open(article_path, "w", encoding="utf-8") as f:
    f.write(f"# TITLE: {clean_title}\n\n{body}\n")

# --- Step 3: 構造化スクリーニング（TADC抽出） ---
def extract_section(section_name, text):
    # 各セクションの内容を次のヘッダーが来るまで抜き出す正規表現
    pattern = rf"# {section_name}\n(.*?)(?=\n#|$)"
    res = re.search(pattern, text, re.DOTALL)
    return res.group(1).strip() if res else ""

all_files = sorted([f for f in os.listdir(tag_dir) if f.endswith(".md")], reverse=True)

context_path = f"contexts/ctx_{tag}.md"
header = f"# 🧠 SYSTEM CONTEXT: {tag}\nGenerated: {now_str} (UTC)\n"
header += "※過去の決定事項（Conclusion）と要旨（Abstract）の凝縮版\n\n---\n\n"

compiled_body = ""
# 文字数制限（2000文字）に収まるまで、新しい順にABSTRACTとCONCLUSIONを拾う
for f_name in all_files:
    with open(os.path.join(tag_dir, f_name), "r", encoding="utf-8") as f:
        content = f.read()
        
        t_match = re.search(r"# TITLE: (.*?)\n", content)
        title = t_match.group(1) if t_match else f_name
        abstract = extract_section("ABSTRACT", content)
        conclusion = extract_section("CONCLUSION", content)
        
        if not abstract and not conclusion:
            continue # 両方空なら無視
            
        entry = f"### 📄 {title}\n"
        if abstract: entry += f"**【ABSTRACT】**\n{abstract}\n\n"
        if conclusion: entry += f"**【CONCLUSION】**\n{conclusion}\n\n"
        entry += "---\n\n"
        
        # 文字数チェック
        if len(header) + len(compiled_body) + len(entry) < 2000:
            compiled_body += entry
        else:
            break

# 書き込み
with open(context_path, "w", encoding="utf-8") as f:
    f.write(header + compiled_body)

print(f"✅ Context compiled: {tag} (TADC format)")
