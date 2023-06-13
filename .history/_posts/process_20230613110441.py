import os
import glob
import re

# 城市列表
cities = [
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
    "全国甲",
    "全国乙",
    "全国新高考",
    "全国高职单招",]



# 定义函数，检查文件内容并添加城市标签
def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 检查文件中的城市名字
    city_found = []
    for city in cities:
        if any(city in line for line in lines):
            city_found.append(city)

    # 读取文件的YAML头部
    front_matter = '\n'.join(line for line in lines if line.strip() != '---')
    tags = yaml.load(front_matter, Loader=yaml.FullLoader).get('tags', [])
    tags = set(tag for tag in tags if tag not in cities)

    # 合并新发现的和现有的城市标签
    tags.update(city_found)

    if tags:
        with open(filename, 'w', encoding='utf-8') as f:
            in_front_matter = False
            for line in lines:
                # 查找YAML头部信息的开始和结束
                if line.strip() == '---':
                    if in_front_matter:
                        # 如果有标签，添加标签
                        if tags:
                            tags_line = "tags: [" + ", ".join(tags) + "]\n"
                            f.write(tags_line)
                    in_front_matter = not in_front_matter

                f.write(line)

# 遍历目录中的所有Markdown文件
for filename in glob.glob('*.md'):  # 修改为你的文件路径
    process_file(filename)
