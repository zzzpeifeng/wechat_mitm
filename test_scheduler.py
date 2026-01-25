#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试定时任务功能
"""
import time
from core.utils.scheduler_manager import SchedulerManager


def test_job():
    """测试任务函数"""
    print(f"执行测试任务: {time.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    print("开始测试定时任务功能...")
    
    # 创建调度器管理器
    scheduler_manager = SchedulerManager()
    
    # 添加一个每分钟执行的任务用于测试（更频繁以便快速验证）
    scheduler_manager.add_scheduled_job(
        func=test_job,
        job_id='test_job',
        hours_interval=1,  # 每1小时执行一次
        name='测试任务'
    )
    
    print("启动调度器...")
    scheduler_manager.start_scheduler()
    
    print("调度器已启动，等待任务执行...")
    print("任务将在每小时的第0分钟执行")
    print("按 Ctrl+C 停止测试")
    
    try:
        # 保持程序运行，观察任务是否重复执行
        while True:
            time.sleep(10)  # 每10秒检查一次
            print(f"调度器状态: {'运行中' if scheduler_manager.is_running else '已停止'}")
            print(f"任务状态: {'已调度' if scheduler_manager.is_job_scheduled('test_job') else '未调度'}")
    except KeyboardInterrupt:
        print("\n停止测试...")
        scheduler_manager.stop_scheduler()
        print("调度器已停止")


if __name__ == "__main__":
    main()