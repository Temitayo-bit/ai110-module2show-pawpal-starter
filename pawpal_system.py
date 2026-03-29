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
    recurring: bool = False
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
