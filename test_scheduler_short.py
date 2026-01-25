#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试定时任务功能 - 短间隔测试
"""
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import atexit


def test_job():
    """测试任务函数"""
    print(f"执行测试任务: {time.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    print("开始测试定时任务功能（短间隔）...")
    
    # 创建调度器
    scheduler = BackgroundScheduler()
    
    # 添加一个每分钟执行的任务用于测试
    scheduler.add_job(
        func=test_job,
        trigger=IntervalTrigger(minutes=1),  # 每1分钟执行一次，便于测试
        id='test_job_interval',
        name='测试任务-间隔',
        max_instances=1
    )
    
    # 添加使用CronTrigger的任务（使用修复后的方式）
    scheduler.add_job(
        func=test_job,
        trigger=CronTrigger(minute='*/1'),  # 每分钟执行一次
        id='test_job_cron',
        name='测试任务-cron',
        max_instances=1
    )
    
    print("启动调度器...")
    scheduler.start()
    
    print("调度器已启动，等待任务执行...")
    print("任务将在每分钟的0秒执行")
    print("按 Ctrl+C 停止测试")
    
    try:
        # 保持程序运行，观察任务是否重复执行
        start_time = time.time()
        while True:
            time.sleep(10)  # 每10秒检查一次
            elapsed = time.time() - start_time
            print(f"已运行 {int(elapsed)} 秒，调度器状态: {'运行中' if scheduler.running else '已停止'}")
            
            # 运行1分钟就退出测试
            if elapsed > 120:  # 2分钟后自动退出
                break
    except KeyboardInterrupt:
        print("\n停止测试...")
    
    scheduler.shutdown(wait=True)
    print("调度器已停止")


if __name__ == "__main__":
    main()