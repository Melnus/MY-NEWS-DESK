import os
import re
import datetime

# 1. データの取得
title_raw = os.getenv("ISSUE_TITLE", "No Title").strip()
body = os.getenv("ISSUE_BODY", "No Body").strip()

# フォルダ作成
os.makedirs("contexts", exist_ok=True)
os.makedirs("articles", exist_ok=True)

# --- Step 1: タグ選別 ---
match = re.match(r"^\[([A-Za-z0-9_-]+)\]", title_raw)
tag = match.group(1).upper() if match else "IDEAS"
clean_title = title_raw[match.end():].strip() if match else title_raw

tag_dir = f"articles/{tag}"
os.makedirs(tag_dir, exist_ok=True)

# --- Step 2: 今回の記事を保存（生ログ） ---
now_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
safe_file_title = re.sub(r'[\\/*?:"<>|]', '', clean_title).replace(' ', '_')

# 💡 ファイル名がLinuxの255バイト制限を突破しないよう、先頭40文字でカットする
safe_file_title_short = safe_file_title[:40]

# ファイル名にはカットした短い名前を使う
article_filename = f"{now_str}_{safe_file_title_short}.md"
article_path = os.path.join(tag_dir, article_filename)

with open(article_path, "w", encoding="utf-8") as f:
    # ファイルの「中身」には、省略されていない元の完全なタイトルを記録する
    f.write(f"# TITLE: {clean_title}\n\n{body}\n")

print(f"✅ Saved new article: {article_path}")

# --- Step 3: 【全フォルダ精査】構造化スクリーニング（全TADC一斉再構築） ---
def extract_section(section_name, text):
    # 見出し前後の見えないスペース（\s*）を許容
    pattern = rf"#\s*{section_name}\s*\n(.*?)(?=\n#|$)"
    res = re.search(pattern, text, re.DOTALL)
    return res.group(1).strip() if res else ""

# articles/ の下にあるすべてのタグフォルダをループ処理
for current_tag in os.listdir("articles"):
    current_tag_dir = os.path.join("articles", current_tag)
    
    # フォルダでなければスキップ
    if not os.path.isdir(current_tag_dir):
        continue

    # 新しい順にファイルを並べ替え
    all_files = sorted([f for f in os.listdir(current_tag_dir) if f.endswith(".md")], reverse=True)
    
    context_path = f"contexts/ctx_{current_tag}.md"
    header = f"# 🧠 SYSTEM CONTEXT: {current_tag}\nGenerated: {now_str} (UTC)\n"
    header += "※過去の決定事項（Conclusion）と要旨（Abstract）の凝縮版\n\n---\n\n"
    
    compiled_body = ""
    # 文字数制限（2000文字）に収まるまで、新しい順に抽出
    for f_name in all_files:
        with open(os.path.join(current_tag_dir, f_name), "r", encoding="utf-8") as f:
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

    # 各タグのコンテキストを上書き保存
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(header + compiled_body)
    
    print(f"🔄 Rebuilt context: {current_tag}")

print("✅ All contexts successfully compiled.")
