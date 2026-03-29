"""Unit tests for basic PawPal task and pet behavior."""

from pawpal_system import Pet, Priority, TaskStatus


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
