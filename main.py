"""Small CLI demo that builds and prints today's PawPal schedule."""

from pawpal_system import (
	Availability,
	Constraints,
	Owner,
	Pet,
	Preferences,
	Priority,
	Scheduler,
	TaskStatus,
	TimeWindow,
)


def format_minutes(total_minutes: int) -> str:
	"""Convert minutes after midnight to HH:MM format."""
	hours = total_minutes // 60
	minutes = total_minutes % 60
	return f"{hours:02d}:{minutes:02d}"


def find_pet_name_for_task(owner: Owner, task_to_match) -> str:
	"""Return the pet name that owns the given task object."""
	for pet in owner.pets:
		if task_to_match in pet.default_tasks:
			return pet.name
	return "Unknown Pet"


def main() -> None:
	# Build two pets under one owner.
	luna = Pet(name="Luna", species="Cat", age=4)
	max_pet = Pet(name="Max", species="Dog", age=6)

	# Add tasks intentionally out of chronological order.
	playtime = max_pet.create_task("Playtime", duration=25, priority=Priority.LOW)
	playtime.time = "18:00"
	playtime.preferred_window = TimeWindow(start_minutes=18 * 60, end_minutes=19 * 60)

	feed_luna = luna.create_task("Feed Luna", duration=20, priority=Priority.HIGH)
	feed_luna.time = "07:30"
	feed_luna.preferred_window = TimeWindow(start_minutes=7 * 60, end_minutes=8 * 60)

	walk_max = max_pet.create_task("Walk Max", duration=30, priority=Priority.MEDIUM)
	walk_max.time = "12:00"
	walk_max.preferred_window = TimeWindow(start_minutes=12 * 60, end_minutes=13 * 60)

	groom_luna = luna.create_task("Brush Luna", duration=10, priority=Priority.MEDIUM)
	groom_luna.time = "09:15"
	groom_luna.preferred_window = TimeWindow(start_minutes=9 * 60, end_minutes=10 * 60)
	groom_luna.mark_completed()

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=6 * 60, end_minutes=20 * 60)),
		preferences=Preferences(prefers_morning=True, max_daily_minutes=180),
	)
	owner.add_pet(luna)
	owner.add_pet(max_pet)

	scheduler = Scheduler(
		owner=owner,
		day_window=TimeWindow(start_minutes=6 * 60, end_minutes=20 * 60),
		constraints=Constraints(max_daily_minutes=180),
	)

	all_tasks = [task for pet in owner.pets for task in pet.default_tasks]

	print("\nAll Tasks (creation order)")
	for task in all_tasks:
		pet_name = find_pet_name_for_task(owner, task)
		print(f"- {task.time} | {pet_name}: {task.title} [{task.status.value}]")

	print("\nTasks Sorted by Time (Scheduler.sort_by_time)")
	for task in scheduler.sort_by_time(all_tasks):
		pet_name = find_pet_name_for_task(owner, task)
		print(f"- {task.time} | {pet_name}: {task.title} [{task.status.value}]")

	print("\nLuna Tasks (Scheduler.filter_tasks by pet_name)")
	for task in scheduler.filter_tasks(tasks=all_tasks, pet_name="Luna"):
		print(f"- {task.time} | {task.title} [{task.status.value}]")

	print("\nCompleted Tasks (Scheduler.filter_tasks by status)")
	for task in scheduler.filter_tasks(tasks=all_tasks, status=TaskStatus.COMPLETED):
		pet_name = find_pet_name_for_task(owner, task)
		print(f"- {task.time} | {pet_name}: {task.title} [{task.status.value}]")

	print("\nPending Tasks for Max (combined filters)")
	for task in scheduler.filter_tasks(
		tasks=all_tasks,
		status=TaskStatus.PENDING,
		pet_name="Max",
	):
		print(f"- {task.time} | {task.title} [{task.status.value}]")

	# Force two tasks to the same scheduled time to demo conflict warnings.
	feed_luna.schedule(start_minutes=8 * 60)
	walk_max.schedule(start_minutes=8 * 60)

	print("\nConflict Check (same scheduled time)")
	conflict_warnings = scheduler.detect_schedule_conflicts([feed_luna, walk_max])
	if not conflict_warnings:
		print("No conflicts detected.")
	else:
		for warning in conflict_warnings:
			print(f"- {warning}")

	plan = scheduler.build_plan(owner)

	print("\nToday's Schedule")
	if not plan.tasks:
		print("No tasks were scheduled today.")
		return

	for task in plan.tasks:
		start = task.scheduled_start if task.scheduled_start is not None else 0
		end = start + task.duration_minutes
		pet_name = find_pet_name_for_task(owner, task)
		print(
			f"- {format_minutes(start)}-{format_minutes(end)} | "
			f"{pet_name}: {task.title} ({task.priority.value})"
		)


if __name__ == "__main__":
	main()
