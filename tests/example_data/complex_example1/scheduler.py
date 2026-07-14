import asyncio

from logger import create_logger
from models import Job
from utils.cache import expensive_lookup


class Scheduler:
    def __init__(self, plugin):
        self.plugin = plugin
        self.logger = create_logger("scheduler")

    async def execute(self, job: Job):

        self.logger.info("Processing %s", job.id)

        cached = expensive_lookup(job.payload)

        result = await self.plugin.process(cached)

        self.logger.info("Finished %s", job.id)

        return result

    async def run(self, jobs):

        tasks = [
            asyncio.create_task(self.execute(job))
            for job in jobs
        ]

        return await asyncio.gather(*tasks)
