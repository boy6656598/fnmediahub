import json
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()


class TaskScheduler:
    def __init__(self, db):
        self.db = db
        self.scheduler = scheduler

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    async def setup_clean_task(self, user_id: int, config: dict):
        from app.models.clean_task import CleanTask
        from app.models.user import User
        import asyncio

        task = self.db.query(CleanTask).filter(
            CleanTask.user_id == user_id,
            CleanTask.task_type == "transfer_clean"
        ).first()

        if not task:
            task = CleanTask(
                user_id=user_id,
                task_type="transfer_clean"
            )
            self.db.add(task)

        task.set_config(config)
        task.status = "scheduled"
        self.db.commit()

        job_id = f"clean_task_{user_id}"

        existing_job = self.scheduler.get_job(job_id)
        if existing_job:
            self.scheduler.remove_job(job_id)

        schedule_type = config.get("schedule_type", "daily")
        hour = config.get("hour", 3)
        keep_count = config.get("keep_count", 5)

        if schedule_type == "daily":
            self.scheduler.add_job(
                self._execute_clean_task,
                CronTrigger(hour=hour, minute=0),
                args=[user_id, config],
                id=job_id,
                replace_existing=True
            )
        elif schedule_type == "weekly":
            day_of_week = config.get("day_of_week", "sun")
            self.scheduler.add_job(
                self._execute_clean_task,
                CronTrigger(day_of_week=day_of_week, hour=hour, minute=0),
                args=[user_id, config],
                id=job_id,
                replace_existing=True
            )
        elif schedule_type == "monthly":
            day_of_month = config.get("day_of_month", 1)
            self.scheduler.add_job(
                self._execute_clean_task,
                CronTrigger(day=day_of_month, hour=hour, minute=0),
                args=[user_id, config],
                id=job_id,
                replace_existing=True
            )

    async def _execute_clean_task(self, user_id: int, config: dict):
        from app.models.user import User
        from app.services.disks.fnnas_client import FnNASClient

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        disk_config = user.get_disk_config()
        transfer_dir = config.get("transfer_dir", "/media/转存")
        keep_count = config.get("keep_count", 5)

        try:
            fnnas_client = FnNASClient(
                host=disk_config.get("host", ""),
                token=disk_config.get("token", "")
            )

            files = await fnnas_client.list_files(transfer_dir)
            files.sort(key=lambda x: x.get("mtime", 0))

            if len(files) > keep_count:
                for f in files[:-keep_count]:
                    await fnnas_client.delete_file(f.get("path"))

            task = self.db.query(CleanTask).filter(
                CleanTask.user_id == user_id,
                CleanTask.task_type == "transfer_clean"
            ).first()

            if task:
                task.last_run = datetime.utcnow()
                self.db.commit()

        except Exception as e:
            print(f"Clean task failed: {e}")

    async def execute_clean_now(self, user_id: int) -> dict:
        from app.models.clean_task import CleanTask

        task = self.db.query(CleanTask).filter(
            CleanTask.user_id == user_id,
            CleanTask.task_type == "transfer_clean"
        ).first()

        if not task:
            return {"success": False, "message": "Task not found"}

        config = task.get_config()
        await self._execute_clean_task(user_id, config)

        return {"success": True, "message": "Clean task executed"}

    async def clear_security_code(self, user_id: int) -> dict:
        from app.models.user import User
        from app.services.disks.client_115 import Client115

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found"}

        if user.disk_type != "115":
            return {"success": False, "message": "Not a 115 user"}

        disk_config = user.get_disk_config()
        client = Client115()

        uid = disk_config.get("uid")
        token = disk_config.get("token")

        if uid and token:
            await client.login_with_token(uid, token)
            result = await client.clear_security()
            return result

        return {"success": False, "message": "Not logged in to 115"}


task_scheduler: Optional[TaskScheduler] = None


def get_task_scheduler(db):
    global task_scheduler
    if task_scheduler is None:
        task_scheduler = TaskScheduler(db)
    return task_scheduler
