#!/usr/bin/env python3
"""
自动翻译博客文章脚本
使用 OpenAI API 将中文文章翻译成英文

使用方法:
    python translate_posts.py "_posts/2025-01-11-example.md _posts/2025-01-10-another.md"
"""

import os
import sys
from pathlib import Path

import frontmatter
import openai

# 初始化 OpenAI 客户端
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

if not api_key:
    print("Error: OPENAI_API_KEY not set")
    sys.exit(1)

client = openai.OpenAI(api_key=api_key)


def translate_with_gpt(text: str, source_lang: str = "Chinese", target_lang: str = "English") -> str:
    """
    使用 GPT 翻译文本
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following {source_lang} text to {target_lang}. "
                    "Keep the tone, style, and formatting (including markdown syntax). "
                    "Only return the translated text without any explanation."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error translating with GPT: {e}")
        raise


def translate_frontmatter(fm: dict, target_lang: str = "English") -> dict:
    """
    翻译 frontmatter 中的字段（title, excerpt, categories, tags 等）
    """
    translated = fm.copy()

    fields_to_translate = ["title", "excerpt", "description"]

    for field in fields_to_translate:
        if field in translated and isinstance(translated[field], str):
            try:
                print(f"  Translating {field}...", end=" ", flush=True)
                translated[field] = translate_with_gpt(translated[field], target_lang=target_lang)
                print("✓")
            except Exception as e:
                print(f"✗ (Error: {e})")
                # 保持原文

    return translated


def generate_english_filename(original_path: str) -> str:
    """
    生成英文文章的文件名
    原: _posts/2025-01-11-example.md
    新: _posts/2025-01-11/en/example.md
    """
    path = Path(original_path)

    # 提取日期前缀 (YYYY-MM-DD)
    stem = path.stem  # "2025-01-11-example"
    parts = stem.split("-", 3)

    if len(parts) >= 4:
        date_prefix = "-".join(parts[:3])  # "2025-01-11"
        filename = "-".join(parts[3:])  # "example"
    else:
        date_prefix = stem
        filename = "post"

    # 新路径: _posts/2025-01-11/en/example.md
    new_path = path.parent / date_prefix / "en" / f"{filename}.md"
    return str(new_path)


def process_post(post_path: str) -> bool:
    """
    处理单个文章：翻译内容和 frontmatter，生成英文版本
    """
    try:
        post_path = Path(post_path)

        if not post_path.exists():
            print(f"⚠ File not found: {post_path}")
            return False

        print(f"\n📄 Processing: {post_path}")

        # 读取原文章
        with open(post_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # 翻译内容
        print("  Translating content...", end=" ", flush=True)
        translated_content = translate_with_gpt(post.content)
        print("✓")

        # 翻译 frontmatter
        print("  Translating metadata...")
        translated_fm = translate_frontmatter(post.metadata)

        # 生成英文版本文件名
        en_path = Path(generate_english_filename(str(post_path)))
        en_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入英文文章
        en_post = frontmatter.Post(translated_content, **translated_fm)
        with open(en_path, "w", encoding="utf-8") as f:
            frontmatter.dump(en_post, f)

        print(f"  ✓ Saved to: {en_path}")
        return True

    except Exception as e:
        print(f"  ✗ Error processing {post_path}: {e}")
        return False


def main():
    """
    主函数：处理所有传入的文章
    """
    if len(sys.argv) < 2:
        print("Usage: python translate_posts.py 'file1.md file2.md ...'")
        sys.exit(1)

    # 解析文件列表
    files_str = sys.argv[1].strip()
    files = [f.strip() for f in files_str.split() if f.strip()]

    if not files:
        print("No files to process")
        return

    print(f"🚀 Starting translation of {len(files)} post(s)...")
    print(f"Using model: {model}")

    success_count = 0
    for file in files:
        if process_post(file):
            success_count += 1

    print(f"\n✅ Translation complete: {success_count}/{len(files)} posts translated successfully")


if __name__ == "__main__":
    main()
    main()
