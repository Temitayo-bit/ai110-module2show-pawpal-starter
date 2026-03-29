"""Unit tests for basic PawPal task and pet behavior."""

from pawpal_system import Availability, Owner, Pet, Preferences, Priority, Scheduler, Task, TaskStatus, TimeWindow


def test_task_completion_changes_status_to_completed() -> None:
	pet = Pet(name="Luna", species="Cat", age=4)
	task = pet.create_task(title="Feed Luna", duration=15, priority=Priority.HIGH)

	task.mark_completed()

	assert task.status == TaskStatus.COMPLETED


def test_adding_task_increases_pet_task_count() -> None:
	pet = Pet(name="Max", species="Dog", age=6)

	start_count = len(pet.default_tasks)
	pet.create_task(title="Morning Walk", duration=30, priority=Priority.MEDIUM)

	assert len(pet.default_tasks) == start_count + 1


def test_sort_by_time_orders_hhmm_strings() -> None:
	scheduler = Scheduler()
	tasks = [
		Task(
			title="Noon walk",
			description="Walk",
			duration_minutes=30,
			priority=Priority.MEDIUM,
			preferred_window=TimeWindow(start_minutes=0, end_minutes=24 * 60),
			time="12:30",
		),
		Task(
			title="Morning feed",
			description="Feed",
			duration_minutes=15,
			priority=Priority.HIGH,
			preferred_window=TimeWindow(start_minutes=0, end_minutes=24 * 60),
			time="08:05",
		),
		Task(
			title="Evening meds",
			description="Medication",
			duration_minutes=10,
			priority=Priority.HIGH,
			preferred_window=TimeWindow(start_minutes=0, end_minutes=24 * 60),
			time="18:00",
		),
	]

	sorted_tasks = scheduler.sort_by_time(tasks)

	assert [task.time for task in sorted_tasks] == ["08:05", "12:30", "18:00"]


def test_filter_tasks_by_status_returns_only_matching_status() -> None:
	pet = Pet(name="Luna", species="Cat", age=4)
	pending_task = pet.create_task(title="Feed", duration=15, priority=Priority.HIGH)
	completed_task = pet.create_task(title="Brush", duration=10, priority=Priority.LOW)
	completed_task.mark_completed()

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(pet)

	scheduler = Scheduler(owner=owner)
	filtered = scheduler.filter_tasks(status=TaskStatus.COMPLETED)

	assert filtered == [completed_task]
	assert pending_task not in filtered


def test_filter_tasks_by_pet_name_returns_only_that_pet_tasks() -> None:
	luna = Pet(name="Luna", species="Cat", age=4)
	max_pet = Pet(name="Max", species="Dog", age=6)
	luna_task = luna.create_task(title="Feed Luna", duration=15, priority=Priority.HIGH)
	max_pet.create_task(title="Walk Max", duration=30, priority=Priority.MEDIUM)

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(luna)
	owner.add_pet(max_pet)

	scheduler = Scheduler(owner=owner)
	filtered = scheduler.filter_tasks(pet_name="Luna")

	assert filtered == [luna_task]


def test_mark_task_completed_creates_next_daily_recurring_instance() -> None:
	pet = Pet(name="Luna", species="Cat", age=4)
	task = pet.create_task(title="Feed Luna", duration=15, priority=Priority.HIGH)
	task.recurring = True
	task.recurrence = "daily"
	task.time = "07:30"

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(pet)

	scheduler = Scheduler(owner=owner)
	next_task = scheduler.mark_task_completed(task)

	assert task.status == TaskStatus.COMPLETED
	assert next_task is not None
	assert next_task.title == "Feed Luna"
	assert next_task.status == TaskStatus.PENDING
	assert next_task.recurrence == "daily"
	assert next_task in pet.default_tasks


def test_mark_task_completed_creates_next_weekly_recurring_instance() -> None:
	pet = Pet(name="Max", species="Dog", age=6)
	task = pet.create_task(title="Weekly Groom", duration=30, priority=Priority.MEDIUM)
	task.recurring = True
	task.recurrence = "weekly"

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(pet)

	scheduler = Scheduler(owner=owner)
	next_task = scheduler.mark_task_completed(task)

	assert next_task is not None
	assert next_task.recurrence == "weekly"
	assert next_task.title == "Weekly Groom"


def test_mark_task_completed_non_recurring_creates_no_new_task() -> None:
	pet = Pet(name="Mochi", species="Cat", age=2)
	task = pet.create_task(title="One-time Vet Call", duration=10, priority=Priority.HIGH)

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(pet)

	scheduler = Scheduler(owner=owner)
	next_task = scheduler.mark_task_completed(task)

	assert task.status == TaskStatus.COMPLETED
	assert next_task is None


def test_detect_schedule_conflicts_returns_warning_for_same_pet_overlap() -> None:
	pet = Pet(name="Luna", species="Cat", age=4)
	first = pet.create_task(title="Feed", duration=30, priority=Priority.HIGH)
	second = pet.create_task(title="Medication", duration=20, priority=Priority.HIGH)
	first.schedule(480)
	second.schedule(495)

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(pet)

	scheduler = Scheduler(owner=owner)
	warnings = scheduler.detect_schedule_conflicts([first, second])

	assert len(warnings) == 1
	assert "Warning: Conflict detected" in warnings[0]
	assert "Feed" in warnings[0]
	assert "Medication" in warnings[0]
	assert "Luna" in warnings[0]


def test_detect_schedule_conflicts_returns_warning_for_different_pet_overlap() -> None:
	luna = Pet(name="Luna", species="Cat", age=4)
	max_pet = Pet(name="Max", species="Dog", age=6)
	luna_task = luna.create_task(title="Feed Luna", duration=30, priority=Priority.HIGH)
	max_task = max_pet.create_task(title="Walk Max", duration=30, priority=Priority.MEDIUM)
	luna_task.schedule(600)
	max_task.schedule(610)

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(luna)
	owner.add_pet(max_pet)

	scheduler = Scheduler(owner=owner)
	warnings = scheduler.detect_schedule_conflicts([luna_task, max_task])

	assert len(warnings) == 1
	assert "Luna" in warnings[0]
	assert "Max" in warnings[0]


def test_detect_schedule_conflicts_returns_empty_when_no_overlap() -> None:
	pet = Pet(name="Luna", species="Cat", age=4)
	first = pet.create_task(title="Feed", duration=20, priority=Priority.HIGH)
	second = pet.create_task(title="Play", duration=20, priority=Priority.MEDIUM)
	first.schedule(480)
	second.schedule(500)

	owner = Owner(
		name="Alex",
		contact_email="alex@example.com",
		availability=Availability(day_window=TimeWindow(start_minutes=0, end_minutes=24 * 60)),
		preferences=Preferences(),
	)
	owner.add_pet(pet)

	scheduler = Scheduler(owner=owner)
	warnings = scheduler.detect_schedule_conflicts([first, second])

	assert warnings == []
