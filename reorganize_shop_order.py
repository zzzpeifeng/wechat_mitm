#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重新组织门店排序，将名称相似的门店分组并排在一起
"""

import json
import os
from collections import defaultdict


def reorganize_shop_order(input_path, output_path):
    """重新组织门店排序，将名称相似的门店分组"""
    # 读取原始的门店排序文件
    with open(input_path, 'r', encoding='utf-8') as f:
        shop_order_dict = json.load(f)
    
    # 定义关键词分组规则
    keyword_groups = [
        ("查理熊", "charlie_bear"),
        ("乐游", "leyou"),
        ("青鸟", "qingniao"),
        ("闹他", "naota"),
        ("小男人", "xiaonannan"),
        ("魔杰", "mojie"),
        ("蜗牛快跑", "woniu"),
        ("先锋", "xianfeng"),
        ("涵度", "handu"),
        ("天际壹号", "tianji"),
        ("星海", "xinghai"),
        ("极夜", "jiye"),
        ("斑马", "banma"),
        ("悟空", "wukong"),
        ("先锋", "xianfeng"),
        ("天音", "tianyin"),
        ("四季", "siji"),
        ("新潮", "xinchao"),
        ("鲸羽", "jingyu"),
        ("蜂巢", "fengchao"),
        ("八度", "baidu"),
        ("巅峰", "dianfeng"),
        ("伊时代", "yishidai"),
        ("街角", "jiejiao"),
        ("龙城", "longcheng"),
        ("山西", "shanxi"),
        ("内蒙古", "neimenggu"),
        ("运城", "yuncheng"),
        ("孝义", "xiaoyi"),
        ("临汾", "linfen"),
        ("文安", "wenan"),
        ("太原", "taiyuan"),  # 可能包含在门店名中
    ]
    
    # 为每个门店分配分组
    grouped_shops = defaultdict(list)
    ungrouped_shops = []
    
    for shop_name, order in shop_order_dict.items():
        assigned = False
        
        # 检查是否属于某个关键词分组
        for keyword, group_name in keyword_groups:
            if keyword in shop_name:
                grouped_shops[group_name].append((order, shop_name))
                assigned = True
                break
        
        if not assigned:
            ungrouped_shops.append((order, shop_name))
    
    # 对每个分组内的门店按原始顺序排序
    for group_name in grouped_shops:
        grouped_shops[group_name].sort(key=lambda x: x[0])  # 按原始顺序排序
    
    # 对未分组的门店按原始顺序排序
    ungrouped_shops.sort(key=lambda x: x[0])
    
    # 生成新的排序字典
    new_shop_order = {}
    current_index = 0
    
    # 按分组顺序添加门店
    group_priority = [
        "charlie_bear", "leyou", "qingniao", "naota", "xiaonannan", 
        "mojie", "woniu", "xianfeng", "handu", "tianji", "xinghai", 
        "jiye", "banma", "wukong", "tianyin", "siji", "xinchao", 
        "jingyu", "fengchao", "baidu", "dianfeng", "yishidai", 
        "jiejiao", "longcheng", "shanxi", "neimenggu", "yuncheng", 
        "xiaoyi", "linfen", "wenan"
    ]
    
    # 首先按优先级添加分组
    for group_name in group_priority:
        if group_name in grouped_shops:
            for _, shop_name in grouped_shops[group_name]:
                new_shop_order[shop_name] = current_index
                current_index += 1
    
    # 添加剩余的分组（不在优先级列表中的）
    for group_name in grouped_shops:
        if group_name not in group_priority:
            for _, shop_name in grouped_shops[group_name]:
                new_shop_order[shop_name] = current_index
                current_index += 1
    
    # 最后添加未分组的门店
    for _, shop_name in ungrouped_shops:
        new_shop_order[shop_name] = current_index
        current_index += 1
    
    # 保存新的排序文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_shop_order, f, ensure_ascii=False, indent=2)
    
    print(f"已重新组织门店排序，保存至: {output_path}")
    print(f"总共包含 {len(new_shop_order)} 个门店")
    
    # 打印分组统计信息
    print("\n分组统计:")
    for group_name in group_priority:
        if group_name in grouped_shops:
            print(f"  {group_name}: {len(grouped_shops[group_name])} 个门店")
    
    print(f"  未分组: {len(ungrouped_shops)} 个门店")
    
    return new_shop_order


def display_grouped_shops(shop_order_dict):
    """显示分组后的门店名称，便于检查"""
    # 按排序顺序获取门店列表
    sorted_shops = sorted(shop_order_dict.items(), key=lambda x: x[1])
    
    print("\n按新排序显示门店（相同关键词的已分组显示）:")
    
    # 定义关键词映射
    keyword_mapping = {
        "查理熊": "charlie_bear",
        "乐游": "leyou",
        "青鸟": "qingniao",
        "闹他": "naota",
        "小男人": "xiaonannan",
        "魔杰": "mojie",
        "蜗牛快跑": "woniu",
        "先锋": "xianfeng",
        "涵度": "handu",
        "天际壹号": "tianji",
        "星海": "xinghai",
        "极夜": "jiye",
        "斑马": "banma",
        "悟空": "wukong",
        "天音": "tianyin",
        "四季": "siji",
        "新潮": "xinchao",
        "鲸羽": "jingyu",
        "蜂巢": "fengchao",
        "八度": "baidu",
        "巅峰": "dianfeng",
        "伊时代": "yishidai",
        "街角": "jiejiao",
        "龙城": "longcheng",
        "山西": "shanxi",
        "内蒙古": "neimenggu",
        "运城": "yuncheng",
        "孝义": "xiaoyi",
        "临汾": "linfen",
        "文安": "wenan"
    }
    
    current_keyword = None
    for shop_name, order in sorted_shops:
        # 检查是否匹配关键词
        matched_keyword = None
        for keyword in keyword_mapping:
            if keyword in shop_name:
                matched_keyword = keyword
                break
        
        if matched_keyword != current_keyword:
            if current_keyword is not None:
                print()  # 空行分隔不同分组
            print(f"[{matched_keyword or '未分组'}分组]")
            current_keyword = matched_keyword
        
        print(f"  {order:3d}: {shop_name}")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(project_root, 'shop_order.json')
    output_path = os.path.join(project_root, 'shop_order_reorganized.json')
    
    if os.path.exists(input_path):
        new_order = reorganize_shop_order(input_path, output_path)
        display_grouped_shops(new_order)
        
        # 询问用户是否要替换原文件
        response = input("\n是否要用新的排序文件替换原来的shop_order.json文件？(y/N): ")
        if response.lower() == 'y':
            import shutil
            shutil.copy2(output_path, input_path)
            print("已替换原文件 shop_order.json")
    else:
        print(f"输入文件不存在: {input_path}")