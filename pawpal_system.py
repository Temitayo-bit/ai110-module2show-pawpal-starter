"""Core domain models and scheduler skeleton for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"


@dataclass
class TimeWindow:
    start_minutes: int
    end_minutes: int


@dataclass
class Availability:
    day_window: TimeWindow


@dataclass
class Preferences:
    prefers_morning: bool = False
    max_daily_minutes: Optional[int] = None


@dataclass
class Task:
    title: str
    description: str
    duration_minutes: int
    priority: Priority
    preferred_window: TimeWindow
    time: str = "00:00"
    recurring: bool = False
    recurrence: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    scheduled_start: Optional[int] = None

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if two tasks overlap in their preferred windows."""
        return not (
            self.preferred_window.end_minutes <= other.preferred_window.start_minutes
            or self.preferred_window.start_minutes >= other.preferred_window.end_minutes
        )

    def mark_completed(self) -> None:
        """Move the task to the completed state."""
        self.status = TaskStatus.COMPLETED

    def schedule(self, start_minutes: int) -> None:
        """Record when the task is scheduled."""
        self.scheduled_start = start_minutes
        self.status = TaskStatus.SCHEDULED


@dataclass
class Pet:
    name: str
    species: str
    age: int
    default_tasks: List[Task] = field(default_factory=list)
    dietary_needs: List[str] = field(default_factory=list)

    def create_task(self, title: str, duration: int, priority: Priority) -> Task:
        """Helper to create a task tied to this pet."""
        task = Task(
            title=title,
            description=f"{self.name} needs this task.",
            duration_minutes=duration,
            priority=priority,
            preferred_window=TimeWindow(start_minutes=0, end_minutes=24 * 60),
        )
        self.default_tasks.append(task)
        return task

    def get_outstanding_tasks(self) -> List[Task]:
        """Return tasks that have not been completed yet."""
        return [task for task in self.default_tasks if task.status != TaskStatus.COMPLETED]


@dataclass
class Owner:
    name: str
    contact_email: str
    availability: Availability
    preferences: Preferences
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Attach a pet to the owner."""
        self.pets.append(pet)

    def set_preferences(self, prefs: Preferences) -> None:
        """Update owner preferences."""
        self.preferences = prefs

    def gather_tasks(self) -> List[Task]:
        """Aggregate tasks from all owned pets."""
        return [task for pet in self.pets for task in pet.get_outstanding_tasks()]


@dataclass
class Constraints:
    max_daily_minutes: Optional[int] = None
    prioritize: Optional[Priority] = None


@dataclass
class Plan:
    tasks: List[Task] = field(default_factory=list)
    explanations: List[str] = field(default_factory=list)


class Explanation:
    def __init__(self, message: str) -> None:
        """Store a human-readable scheduling explanation message."""
        self.message = message


class Scheduler:
    def __init__(
        self,
        owner: Optional[Owner] = None,
        day_window: Optional[TimeWindow] = None,
        constraints: Optional[Constraints] = None,
    ) -> None:
        """Initialize scheduler state with optional owner, window, and constraints."""
        self.owner = owner
        self.day_window = day_window
        self.constraints = constraints or Constraints()
        self.candidates: List[Task] = []
        self.current_plan: Optional[Plan] = None

        if self.owner:
            self._sync_candidates()

    def _sync_candidates(self) -> None:
        """Pull the latest outstanding tasks from the owner context."""
        if self.owner:
            self.candidates = self.owner.gather_tasks()

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort or filter tasks according to priority and constraints."""
        filtered = self._filter_by_constraints(tasks)
        priority_order = {
            Priority.HIGH: 0,
            Priority.MEDIUM: 1,
            Priority.LOW: 2,
        }
        return sorted(filtered, key=lambda t: priority_order.get(t.priority, 3))

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        status: Optional[TaskStatus] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks filtered by optional status and pet name.

        If ``tasks`` is provided, filtering is applied to that explicit list.
        Otherwise, this method falls back to owner tasks (when an owner is
        available) and finally to scheduler candidates.

        Args:
            tasks: Optional task list to filter.
            status: Optional task status to match.
            pet_name: Optional pet name (case-insensitive) to scope tasks.

        Returns:
            A list of tasks matching all provided filters.
        """
        if tasks is not None:
            task_pool = tasks
        elif self.owner:
            task_pool = [task for pet in self.owner.pets for task in pet.default_tasks]
        else:
            task_pool = self.candidates

        filtered = task_pool

        if status is not None:
            filtered = [task for task in filtered if task.status == status]

        if pet_name:
            if not self.owner:
                return []

            pet_lookup = {
                pet.name.lower(): pet.default_tasks
                for pet in self.owner.pets
            }
            owner_pet_tasks = pet_lookup.get(pet_name.lower(), [])
            filtered = [task for task in filtered if task in owner_pet_tasks]

        return filtered

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks in ascending order using ``Task.time`` in HH:MM format.

        The lambda key converts each ``HH:MM`` string into ``(hour, minute)``
        so lexical edge cases (for example, ``"12:00"`` vs ``"08:30"``)
        are handled numerically.

        Args:
            tasks: The tasks to sort.

        Returns:
            A new list sorted by clock time.
        """
        return sorted(tasks, key=lambda task: tuple(map(int, task.time.split(":"))))

    def _find_pet_for_task(self, task_to_match: Task) -> Optional[Pet]:
        """Return the pet that owns a task object, if found.

        Args:
            task_to_match: Task instance to locate in owner pets.

        Returns:
            The matching pet when found, otherwise ``None``.
        """
        if not self.owner:
            return None

        for pet in self.owner.pets:
            if task_to_match in pet.default_tasks:
                return pet
        return None

    def detect_schedule_conflicts(self, tasks: List[Task]) -> List[str]:
        """Detect overlapping scheduled tasks and return warning messages.

        A conflict exists when two scheduled tasks overlap by duration using
        interval logic: ``start_a < end_b`` and ``start_b < end_a``.
        This method is non-blocking and only reports warnings.

        Args:
            tasks: Tasks to scan for overlaps. Tasks without ``scheduled_start``
                are ignored.

        Returns:
            Human-readable warning strings, one per detected conflict.
        """
        warnings: List[str] = []
        scheduled_tasks = [task for task in tasks if task.scheduled_start is not None]

        for index, first_task in enumerate(scheduled_tasks):
            first_start = first_task.scheduled_start if first_task.scheduled_start is not None else 0
            first_end = first_start + first_task.duration_minutes

            for second_task in scheduled_tasks[index + 1 :]:
                second_start = second_task.scheduled_start if second_task.scheduled_start is not None else 0
                second_end = second_start + second_task.duration_minutes

                overlaps = first_start < second_end and second_start < first_end
                if not overlaps:
                    continue

                first_pet = self._find_pet_for_task(first_task)
                second_pet = self._find_pet_for_task(second_task)
                first_pet_name = first_pet.name if first_pet else "Unknown Pet"
                second_pet_name = second_pet.name if second_pet else "Unknown Pet"

                warnings.append(
                    "Warning: Conflict detected between "
                    f"'{first_task.title}' ({first_pet_name}) and "
                    f"'{second_task.title}' ({second_pet_name}) at overlapping times."
                )

        return warnings

    def _create_next_recurring_instance(self, task: Task) -> Optional[Task]:
        """Create the next task instance for supported recurring schedules.

        Only tasks marked recurring with ``daily`` or ``weekly`` recurrence
        create a successor. The new instance starts in pending state.

        Args:
            task: Completed source task.

        Returns:
            A newly created next-occurrence task, or ``None`` when recurrence
            rules do not apply.
        """
        recurrence = (task.recurrence or "").lower()
        if not task.recurring or recurrence not in {"daily", "weekly"}:
            return None

        return Task(
            title=task.title,
            description=task.description,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            preferred_window=task.preferred_window,
            time=task.time,
            recurring=True,
            recurrence=recurrence,
        )

    def mark_task_completed(self, task: Task) -> Optional[Task]:
        """Mark a task complete and optionally create its next recurrence.

        For supported recurring tasks, this method appends a newly created
        next-occurrence instance to the same pet and refreshes scheduler
        candidates. For non-recurring tasks, it only marks completion.

        Args:
            task: Task to complete.

        Returns:
            The newly created recurring task instance when applicable,
            otherwise ``None``.
        """
        task.mark_completed()
        next_task = self._create_next_recurring_instance(task)

        if not next_task:
            return None

        owner_pet = self._find_pet_for_task(task)
        if owner_pet:
            owner_pet.default_tasks.append(next_task)
            self._sync_candidates()
            return next_task

        return None

    def _filter_by_constraints(self, tasks: List[Task]) -> List[Task]:
        """Drop tasks that clearly exceed time limits or the owner's day window."""
        window = self.day_window or (self.owner.availability.day_window if self.owner else None)
        filtered: List[Task] = []
        total_minutes = 0
        max_minutes = (
            self.constraints.max_daily_minutes
            or (self.owner.preferences.max_daily_minutes if self.owner else None)
        )

        for task in tasks:
            if window and (
                task.preferred_window.start_minutes < window.start_minutes
                or task.preferred_window.end_minutes > window.end_minutes
            ):
                continue
            if max_minutes and total_minutes + task.duration_minutes > max_minutes:
                continue
            filtered.append(task)
            total_minutes += task.duration_minutes

        return filtered

    def build_plan(self, owner: Owner, tasks: Optional[List[Task]] = None) -> Plan:
        """Create a daily plan for the owner given available tasks."""
        self.owner = owner
        self._sync_candidates()
        candidate_tasks = tasks or self.candidates
        ranked = self.rank_tasks(candidate_tasks)
        window = self.day_window or owner.availability.day_window
        current_minute = window.start_minutes
        scheduled_tasks: List[Task] = []
        explanations: List[str] = []

        for task in ranked:
            end_minute = current_minute + task.duration_minutes
            if end_minute > window.end_minutes:
                continue
            task.schedule(start_minutes=current_minute)
            scheduled_tasks.append(task)
            explanations.append(self.explain_decision(task).message)
            current_minute = end_minute

        explanations.extend(self.detect_schedule_conflicts(scheduled_tasks))

        plan = Plan(tasks=scheduled_tasks, explanations=explanations)
        self.current_plan = plan
        return plan

    def explain_decision(self, task: Task) -> Explanation:
        """Describe why a task was included or scheduled at a certain time."""
        start = task.scheduled_start or 0
        message = (
            f"{task.title} ({task.priority.value}) scheduled at minute {start} "
            f"for {task.duration_minutes} minutes."
        )
        return Explanation(message=message)
