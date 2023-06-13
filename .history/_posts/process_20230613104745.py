import os
import glob
import re

# 城市列表
provinces_and_municipalities = [
    "北京",
    "天津",
    "上海",
    "重庆",
    "河北",
    "山西",
    "辽宁",
    "吉林",
    "黑龙江",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "海南",
    "四川",
    "贵州",
    "云南",
    "陕西",
    "甘肃",
    "青海",
    "台湾",
    '
]


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
