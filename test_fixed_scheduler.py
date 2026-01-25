#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试修复后的定时任务功能
"""
import time
from core.ui.controllers.all_collector import AllCollector


def mock_log_callback(msg):
    """模拟日志回调"""
    print(f"[LOG] {msg}")


def test_scheduled_task():
    """测试定时任务"""
    print("开始测试修复后的定时任务功能...")
    
    # 创建AllCollector实例
    collector = AllCollector()
    collector.log_callback = mock_log_callback
    
    # 测试立即执行一次任务（用于验证异常处理）
    print("\n测试单次任务执行...")
    try:
        collector.get_all_data()
        print("单次任务执行完成")
    except Exception as e:
        print(f"单次任务执行出错: {e}")
        import traceback
        traceback.print_exc()


def test_scheduler():
    """测试调度器功能"""
    print("\n开始测试定时任务调度器...")
    
    from core.utils.scheduler_manager import SchedulerManager
    
    # 创建调度器管理器
    scheduler_manager = SchedulerManager()
    
    # 添加一个测试任务，使用异常安全的包装函数
    def safe_test_job():
        try:
            print(f"执行测试任务: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"任务执行出错: {e}")
    
    scheduler_manager.add_scheduled_job(
        func=safe_test_job,
        job_id='test_job_safe',
        hours_interval=1,  # 每1小时执行一次
        name='安全测试任务'
    )
    
    print("启动调度器...")
    scheduler_manager.start_scheduler()
    
    print("调度器已启动，等待任务执行...")
    print("任务将在每小时的第0分钟执行")
    print("按 Ctrl+C 停止测试")
    
    try:
        # 保持程序运行，观察任务是否重复执行
        start_time = time.time()
        while True:
            time.sleep(30)  # 每30秒检查一次
            elapsed = time.time() - start_time
            print(f"已运行 {int(elapsed)} 秒，调度器状态: {'运行中' if scheduler_manager.is_running else '已停止'}")
            print(f"任务状态: {'已调度' if scheduler_manager.is_job_scheduled('test_job_safe') else '未调度'}")
            
            # 运行5分钟就退出测试
            if elapsed > 300:  # 5分钟后自动退出
                break
    except KeyboardInterrupt:
        print("\n停止测试...")
    
    scheduler_manager.stop_scheduler()
    print("调度器已停止")


def main():
    # 先测试单次任务执行
    test_scheduled_task()
    
    # 再测试调度器
    test_scheduler()


if __name__ == "__main__":
    main()