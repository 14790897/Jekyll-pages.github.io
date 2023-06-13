import os
import glob
import re

# 城市列表
provinces_and_municipalities = [
    "北京市",
    "天津市",
    "上海市",
    "重庆市",
    "河北省",
    "山西省",
    "辽宁省",
    "吉林省",
    "黑龙江省",
    "江苏省",
    "浙江省",
    "安徽省",
    "福建省",
    "江西省",
    "山东省",
    "河南省",
    "湖北省",
    "湖南省",
    "广东省",
    "海南省",
    "四川省",
    "贵州省",
    "云南省",
    "陕西省",
    "甘肃省",
    "青海省",
    "台湾省"
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
