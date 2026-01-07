# core/utils/scheduler_manager.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit
import logging
import sys

class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
    def start_scheduler(self):
        """启动调度器 - 跨平台兼容"""
        if not self.scheduler.running:
            self.scheduler.start()
            self.is_running = True
            # 确保程序退出时关闭调度器
            atexit.register(lambda: self.stop_scheduler())
            
    def stop_scheduler(self):
        """停止调度器 - 跨平台兼容"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)  # 等待当前任务完成
            self.is_running = False
            
    def add_scheduled_job(self, func, job_id, hours_interval=2, name=None):
        """添加定时任务 - 跨平台兼容"""
        cron_expression = f"0 */{hours_interval} * * *"
        self.scheduler.add_job(
            func=func,
            trigger=CronTrigger.from_crontab(cron_expression),
            id=job_id,
            name=name or f"Job-{job_id}",
            replace_existing=True,
            max_instances=1  # 防止任务重叠执行
        )
        
    def remove_job(self, job_id):
        """移除定时任务 - 跨平台兼容"""
        try:
            self.scheduler.remove_job(job_id)
        except KeyError:
            pass  # 任务不存在，忽略错误
            
    def is_job_scheduled(self, job_id):
        """检查任务状态 - 跨平台兼容"""
        job = self.scheduler.get_job(job_id)
        return job is not None
