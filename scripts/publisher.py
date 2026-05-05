import os
import json

CONTEXTS_DIR = "contexts"
DOCS_DIR = "docs"
MANIFEST_PATH = os.path.join(DOCS_DIR, "manifest.json")

os.makedirs(DOCS_DIR, exist_ok=True)

def generate_manifest():
    """現在存在する全コンテキストをスキャンしてWebサイト用の目次を作る"""
    if not os.path.exists(CONTEXTS_DIR):
        print("No contexts found. Skipping.")
        return

    # contexts/ctx_TAG.md という形式のファイルをすべて取得
    files = [f for f in os.listdir(CONTEXTS_DIR) if f.startswith("ctx_") and f.endswith(".md")]
    
    # タグ名だけを抽出（例: ctx_GAME.md -> GAME）
    tags = sorted([f.replace("ctx_", "").replace(".md", "") for f in files])

    # docs/manifest.json として保存
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(tags, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Web Manifest updated with {len(tags)} projects.")

if __name__ == "__main__":
    generate_manifest()
