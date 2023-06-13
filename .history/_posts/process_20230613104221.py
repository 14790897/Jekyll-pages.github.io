import os
import glob
import re

# 城市列表
cities = ['北京', '上海', '广州', '深圳']

# 定义函数，检查文件内容并添加城市标签
def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 检查文件中的城市名字
    city_found = []
    for city in cities:
        if any(city in line for line in lines):
            city_found.append(city)

    if city_found:
        with open(filename, 'w', encoding='utf-8') as f:
            in_front_matter = False
            for line in lines:
                # 查找YAML头部信息的开始和结束
                if line.strip() == '---':
                    if in_front_matter:
                        # 如果找到城市，添加城市标签
                        for city in city_found:
                            f.write(f'tag: {city}\n')
                    in_front_matter = not in_front_matter

                f.write(line)

# 遍历目录中的所有Markdown文件
for filename in glob.glob('*.md'):  # 修改为你的文件路径
    process_file(filename)
