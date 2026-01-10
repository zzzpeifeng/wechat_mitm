import os
import sys
import json

# 添加项目根目录到Python路径，以便正确导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import pandas as pd
except ImportError:
    print("pandas未安装，请运行 pip install pandas 安装")
    sys.exit(1)

try:
    from openpyxl import load_workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
except ImportError:
    print("openpyxl未安装，请运行 pip install openpyxl 安装")
    sys.exit(1)

from datetime import datetime
import calendar

# 动态导入数据库模块
def get_db_manager():
    from core.utils.database import get_db_manager
    return get_db_manager()


def ensure_result_folder():
    """确保项目根目录存在result文件夹"""
    result_path = os.path.join(os.getcwd(), 'result')
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    return result_path


def get_current_year_month():
    """获取当前年月，格式为yyyy-mm"""
    now = datetime.now()
    return now.strftime('%Y-%m')


def get_current_date():
    """获取当前日期，格式为yyyy-mm-dd"""
    now = datetime.now()
    return now.strftime('%Y-%m-%d')


def prepare_data_for_excel(collection_data):
    """
    准备数据以写入Excel
    :param collection_data: MongoDB中的数据
    :return: DataFrame格式的数据
    """
    if not collection_data or 'data' not in collection_data:
        # 如果没有数据，创建空的数据框架
        hours = [f'{hour}:00' for hour in range(24)]
        df = pd.DataFrame(columns=['门店名称'] + hours)
        return df

    # 提取所有门店名称
    all_shops = set()
    for hour_data in collection_data['data'].values():
        all_shops.update(hour_data.keys())
    
    all_shops = sorted(list(all_shops))  # 排序以保持一致的顺序
    
    # 创建数据框架
    hours = [f'{hour}:00' for hour in range(24)]  # 0:00 到 23:00
    df_data = {'门店名称': all_shops}
    
    # 为每个小时填充数据
    for hour in hours:
        hour_key = hour.split(':')[0].lstrip('0') or '0'  # 去除前导零，例如 '0:00' -> '0'
        hour_column = []
        
        for shop in all_shops:
            # 检查该小时是否有此店铺的数据
            if hour_key in collection_data['data'] and shop in collection_data['data'][hour_key]:
                hour_column.append(collection_data['data'][hour_key][shop])
            else:
                hour_column.append('0 / 0')  # 默认值
        
        df_data[hour] = hour_column
    
    df = pd.DataFrame(df_data)
    return df


def sync_daily_data():
    """主函数：同步每日数据到Excel文件"""
    # 确保result文件夹存在
    result_folder = ensure_result_folder()
    
    # 获取当前年月作为文件名
    year_month = get_current_year_month()
    excel_filename = f"{year_month}.xlsx"
    excel_path = os.path.join(result_folder, excel_filename)
    
    # 获取当前日期作为sheet名
    current_date = get_current_date()
    
    # 获取数据库管理器并连接
    db_manager = get_db_manager()
    if not db_manager.connect():
        print("无法连接到数据库")
        return
    
    try:
        # 从MongoDB获取当天的数据
        collection = db_manager.db['online_rate_new']
        date_data = collection.find_one({"sheet_date": current_date})
        
        # 准备要写入Excel的数据
        excel_data = prepare_data_for_excel(date_data)
        
        # 检查Excel文件是否存在，如果不存在则创建
        if not os.path.exists(excel_path):
            print(f"创建新的Excel文件: {excel_path}")
            # 创建一个新的Excel文件并将数据写入当前日期的sheet
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                excel_data.to_excel(writer, sheet_name=current_date, index=False)
            print(f"已创建文件: {excel_path} 并添加了 {current_date} 工作表，写入了 {len(excel_data)} 行数据")
        else:
            # 文件已存在，使用openpyxl直接操作
            workbook = load_workbook(excel_path)
            
            # 如果sheet已存在，删除它
            if current_date in workbook.sheetnames:
                del workbook[current_date]
            
            # 创建新的worksheet
            worksheet = workbook.create_sheet(title=current_date)
            
            # 将DataFrame转换为行并写入工作表
            for row in dataframe_to_rows(excel_data, index=False, header=True):
                worksheet.append(row)
                
            # 保存工作簿
            workbook.save(excel_path)
            
            print(f"已更新 {excel_path} 中的 {current_date} 工作表，写入了 {len(excel_data)} 行数据")
    finally:
        # 断开数据库连接
        db_manager.disconnect()


if __name__ == "__main__":
    sync_daily_data()