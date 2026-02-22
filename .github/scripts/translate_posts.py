#!/usr/bin/env python3
"""
自动翻译博客文章脚本
使用 OpenAI API 将中文文章翻译成英文

使用方法:
    python translate_posts.py "_posts/2025-01-11-example.md _posts/2025-01-10-another.md"
"""

import json
import os
import sys
from pathlib import Path

import frontmatter
import openai

# 初始化 OpenAI 客户端
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gemini-flash-latest")
base_url = os.getenv("OPENAI_BASE_URL")


if not api_key:
    print("Error: OPENAI_API_KEY not set")
    sys.exit(1)

print(f"API Base URL: {base_url}")
print(f"Model: {model}\n")

client = openai.OpenAI(api_key=api_key, base_url=base_url)


def translate_post_single_call(
    content: str, fm: dict, target_lang: str = "English"
) -> tuple[str, dict] | tuple[None, None]:
    """
    单次调用翻译正文 + frontmatter
    返回 (None, None) 表示翻译失败
    """
    fields_to_translate = ["title", "excerpt", "description"]
    fm_payload = {
        field: fm[field]
        for field in fields_to_translate
        if field in fm and isinstance(fm[field], str)
    }

    payload = {
        "content": content,
        "frontmatter": fm_payload,
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the markdown content and JSON values to the target language. "
                    "Keep markdown formatting, tone, and style. Keep JSON keys unchanged. "
                    "Return ONLY valid JSON with keys: content (string) and frontmatter (object).",
                },
                {
                    "role": "user",
                    "content": f"Target language: {target_lang}\nJSON: {json.dumps(payload, ensure_ascii=False)}",
                },
            ],
            temperature=0.2,
            max_tokens=9000,
        )

        # 调试：检查响应类型
        print(f"\n  [DEBUG] Response type: {type(response)}")

        # 处理不同类型的响应
        if isinstance(response, str):
            print(f"  [DEBUG] Response is string (likely error), content:\n{response[:500]}\n")
            raw = response
        elif hasattr(response, 'choices'):
            raw = response.choices[0].message.content.strip()
            print(f"\n  [DEBUG] API Response (first 500 chars):\n  {raw[:500]}\n")
        else:
            raise ValueError(f"Unexpected response type: {type(response)}")

        # 尝试解析 JSON
        if not raw.startswith("{"):
            # 尝试移除 markdown 代码块包装
            if raw.startswith("```"):
                lines = raw.split("\n")
                # 移除第一行的 ```json 或 ```
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # 移除最后一行的 ```
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                raw = "\n".join(lines).strip()
                print("  [INFO] Removed markdown code block wrapper")

            if not raw.startswith("{"):
                print(f"  [ERROR] Response doesn't start with '{{', starts with: {raw[:50]}")
                raise ValueError(f"Invalid JSON response format. Response starts with: {raw[:100]}")

        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError(f"Invalid JSON response: expected dict, got {type(result)}")
        translated_content = result.get("content", content)
        translated_fm = fm.copy()
        if isinstance(result.get("frontmatter"), dict):
            translated_fm.update(result["frontmatter"])

        # 添加语言标记
        translated_fm["lang"] = "en"

        return translated_content, translated_fm
    except Exception as e:
        print(f"\n  [ERROR] Translation failed: {e}")
        import traceback
        print(f"  [TRACEBACK] {traceback.format_exc()}")
        return None, None  # 翻译失败返回 None


def generate_english_filename(original_path: str) -> str:
    """
    生成英文文章的文件名
    原: _posts/20250111/2025-01-11-example.md
    新: _posts/20250111/2025-01-11-example.en.md
    """
    path = Path(original_path)

    # 在原文件名后添加 .en 后缀
    # 例如: 2025-01-11-example.md -> 2025-01-11-example.en.md
    stem = path.stem  # "2025-01-11-example"
    new_filename = f"{stem}.en{path.suffix}"  # "2025-01-11-example.en.md"

    # 保持在同一目录下
    new_path = path.parent / new_filename
    return str(new_path)


def process_post(post_path: str) -> bool:
    """
    处理单个文章：翻译内容和 frontmatter，生成英文版本
    """
    try:
        path = Path(post_path)

        if not path.exists():
            print(f"⚠ File not found: {path}")
            return False

        # 跳过已经是英文版本的文件
        if path.stem.endswith('.en'):
            print(f"\n⏭️  Skipping (already English): {path}")
            return True

        print(f"\n📄 Processing: {path}")

        # 读取原文章
        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # 为原文添加语言标记（如果还没有）
        if "lang" not in post.metadata:
            post.metadata["lang"] = "zh"
            # 保存更新后的原文
            with open(path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
            print(f"  ℹ️  Added lang: zh to original file")

        # 生成英文版本文件名
        en_path = Path(generate_english_filename(str(path)))

        # 检查英文文件是否已存在
        if en_path.exists():
            print(f"  ℹ️  English version already exists, will overwrite: {en_path}")

        # 单次调用翻译正文 + frontmatter
        print("  Translating content + metadata (single call)...", end=" ", flush=True)
        translated_content, translated_fm = translate_post_single_call(
            post.content, post.metadata
        )

        # 检查翻译是否成功
        if translated_content is None or translated_fm is None:
            print("✗")
            print("  ✗ Translation failed, skipping file creation")
            return False

        print("✓")

        # 写入英文文章
        en_path.parent.mkdir(parents=True, exist_ok=True)
        # 确保 translated_fm 是字典类型
        fm_dict = dict(translated_fm) if translated_fm is not None else {}
        en_post = frontmatter.Post(translated_content, **fm_dict)
        with open(en_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(en_post))

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
