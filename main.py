"""Small CLI demo that builds and prints today's PawPal schedule."""

from pawpal_system import (
	Availability,
	Constraints,
	Owner,
	Pet,
	Preferences,
	Priority,
	Scheduler,
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

	# Add at least three tasks and give each task a different preferred time window.
	feed_luna = luna.create_task("Feed Luna", duration=20, priority=Priority.HIGH)
	feed_luna.preferred_window = TimeWindow(start_minutes=7 * 60, end_minutes=8 * 60)

	walk_max = max_pet.create_task("Walk Max", duration=30, priority=Priority.MEDIUM)
	walk_max.preferred_window = TimeWindow(start_minutes=12 * 60, end_minutes=13 * 60)

	playtime = max_pet.create_task("Playtime", duration=25, priority=Priority.LOW)
	playtime.preferred_window = TimeWindow(start_minutes=18 * 60, end_minutes=19 * 60)

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
	plan = scheduler.build_plan(owner)

	print("Today's Schedule")
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
