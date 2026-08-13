# Simple task manager

tasks: list = []

def show_tasks():
    if not tasks:
        print("No tasks yet.")
        return

    print("\nYour Tasks:")
    for i, task in enumerate(tasks, 1):
        status = "✓" if task["done"] else " "
        print(f"{i}. [{status}] {task['name']}")

def add_task():
    name = input("Enter a task: ")
    tasks.append({"name": name, "done": False})
    print("Task added!")

def complete_task():
    show_tasks()
    if tasks:
        number = int(input("Enter task number: "))
        if 1 <= number <= len(tasks):
            tasks[number - 1]["done"] = True
            print("Task completed!")

while True:
    print("\n--- Task Manager ---")
    print("1. Show tasks")
    print("2. Add task")
    print("3. Complete task")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        show_tasks()
    elif choice == "2":
        add_task()
    elif choice == "3":
        complete_task()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid choice.")
