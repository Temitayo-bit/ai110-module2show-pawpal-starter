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

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if two tasks overlap in their preferred windows."""
        pass

    def mark_completed(self) -> None:
        """Move the task to the completed state."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    default_tasks: List[Task] = field(default_factory=list)
    dietary_needs: List[str] = field(default_factory=list)

    def create_task(self, title: str, duration: int, priority: Priority) -> Task:
        """Helper to create a task tied to this pet."""
        pass

    def get_outstanding_tasks(self) -> List[Task]:
        """Return tasks that have not been completed yet."""
        pass


@dataclass
class Owner:
    name: str
    contact_email: str
    availability: Availability
    preferences: Preferences
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Attach a pet to the owner."""
        pass

    def set_preferences(self, prefs: Preferences) -> None:
        """Update owner preferences."""
        pass

    def gather_tasks(self) -> List[Task]:
        """Aggregate tasks from all owned pets."""
        pass


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
        self.message = message


class Scheduler:
    def __init__(
        self,
        candidates: Optional[List[Task]] = None,
        day_window: Optional[TimeWindow] = None,
        constraints: Optional[Constraints] = None,
    ) -> None:
        self.candidates = candidates or []
        self.day_window = day_window
        self.constraints = constraints or Constraints()
        self.current_plan: Optional[Plan] = None

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort or filter tasks according to priority and constraints."""
        pass

    def build_plan(self, owner: Owner, tasks: List[Task]) -> Plan:
        """Create a daily plan for the owner given available tasks."""
        pass

    def explain_decision(self, task: Task) -> Explanation:
        """Describe why a task was included or scheduled at a certain time."""
        pass
