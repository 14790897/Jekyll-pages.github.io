#!/usr/bin/env python3
# not used
import os
import glob
import shutil
import re
import datetime
import sys

def main():
    # 定义搜索的基础路径 (用户主目录下的 .vscode-server/extensions)
    base_dir = os.path.expanduser("~/.vscode-server/extensions")

    # 定义搜索模式 (匹配 anthropic.claude-code-* 下的 cli.js)
    # 原始路径: .../anthropic.claude-code-*/resources/claude-code/cli.js
    search_pattern = os.path.join(
        base_dir,
        "anthropic.claude-code-*",
        "resources",
        "claude-code",
        "cli.js"
    )

    print("正在搜索 cli.js 文件...")

    # 查找文件
    found_files = glob.glob(search_pattern)

    if not found_files:
        print("错误: 未找到 cli.js 文件")
        sys.exit(1)

    # 获取第一个匹配的文件
    cli_file = found_files[0]
    print(f"找到文件: {cli_file}")

    # 创建备份文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{cli_file}.backup.{timestamp}"

    try:
        # 创建备份
        print(f"创建备份: {backup_file}")
        shutil.copy2(cli_file, backup_file)

        # 读取文件内容
        with open(cli_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 定义要查找的原始字符串（为了更灵活，这里使用简单的子串检查）
        check_str_1 = "You are Claude Code"
        check_str_2 = "You are a Claude"

        if check_str_1 not in content and check_str_2 not in content:
            print("警告: 文件中未找到目标字符串，未做任何修改。")
            sys.exit(1)

        print("正在修改字符串...")

        # 定义替换逻辑
        # 目标替换为的统一字符串
        target_string = "You are Claude Code, Anthropic's official CLI for Claude."

        # 替换 1: 原始的长版本
        pattern1 = r"You are Claude Code, Anthropic's official CLI for Claude, running within the Claude Agent SDK\."
        new_content = re.sub(pattern1, target_string, content)

        # 替换 2: 另一种 agent 描述
        pattern2 = r"You are a Claude agent, built on Anthropic's Claude Agent SDK\."
        new_content = re.sub(pattern2, target_string, new_content)

        # 如果内容有变化才写入
        if new_content != content:
            with open(cli_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("修改完成！")

            # 验证修改结果
            print("\n验证修改结果 (前5处匹配):")
            lines = new_content.splitlines()
            count = 0
            for i, line in enumerate(lines):
                if "You are Claude" in line:
                    print(f"{i+1}: {line.strip()[:100]}...") # 只显示前100个字符避免刷屏
                    count += 1
                    if count >= 5:
                        break
        else:
            print("文件内容未发生改变 (可能已经被修改过)。")

        print(f"\n备份文件保存在: {backup_file}")
        print(f"如需恢复，请运行: cp \"{backup_file}\" \"{cli_file}\"")

    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()