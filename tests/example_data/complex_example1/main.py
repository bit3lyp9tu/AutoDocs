import asyncio

from container import Container
from models import Job
from scheduler import Scheduler


async def main():

    container = Container()

    plugin = container.get("uppercase")

    scheduler = Scheduler(plugin)

    jobs = [
        Job(1, "hello"),
        Job(2, "world"),
        Job(3, "python"),
        Job(4, "asyncio"),
    ]

    results = await scheduler.run(jobs)

    print("\nResults:\n")

    for r in results:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
