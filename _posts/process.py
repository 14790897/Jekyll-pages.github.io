import os
import glob
import re
import yaml

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

years = [str(year) for year in range(2024, 1999, -1)]  # 从2023年到2000年

# 定义函数，检查文件内容并添加城市标签
def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 首先找到YAML头部的结束
    yaml_end_index = 0
    found_first_delimiter = False
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if found_first_delimiter:  # if this is the second delimiter
                yaml_end_index = i
                break
            else:  # if this is the first delimiter
                found_first_delimiter = True
    print('yaml_end_index', yaml_end_index)
    # 从YAML头部结束之后的部分开始检查文件中的城市名字
    city_found = None
    for line in lines[yaml_end_index+1:]:
        for city in cities:
            matches = re.findall(f'{city}', line[:15])
            if any(match == city for match in matches):
                city_found = city
                break  # 当找到第一个城市时，停止循环
        if city_found is not None:
            break

    # 从YAML头部结束之后的部分开始检查文件中的年份
    year_found = None
    for line in lines[yaml_end_index+1:]:
        for year in years:
            matches = re.findall(f'{year}', line[:15])
            if any(match == year for match in matches):
                year_found = year
                break  # 当找到第一个年份时，停止循环
        if year_found is not None:
            break


    tags = set()
    # 合并新发现的和现有的标签
    if city_found:
        tags.add(city_found)
    if year_found:
        tags.add(year_found)
    # print('tags', tags)
    print('city_found', city_found)
    if tags:
        with open(filename, 'w', encoding='utf-8') as f:
            in_front_matter = False
            for line in lines:
                # 查找YAML头部信息的开始和结束
                if line.strip() == '---':
                    if in_front_matter:
                        # 如果有标签，添加标签
                        if tags:
                            tags_line = "tags: [" + ", ".join(map(str, tags)) + "]\n"
                            f.write(tags_line)
                    in_front_matter = not in_front_matter
                # 删除已有的 'tags' 行
                if 'tags:' in line and in_front_matter:
                    continue

                f.write(line)

# 遍历目录中的所有Markdown文件
for filename in glob.glob('2023-06-12*.md'):  # 修改为你的文件路径
    process_file(filename)
    print(filename)
