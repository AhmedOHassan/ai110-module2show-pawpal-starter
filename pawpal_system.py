from dataclasses import dataclass, field
from datetime import date


# ---------------------------------------------------------------------------
# Task — a single care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str                  # Human-readable label, e.g. "morning walk"
    category: str              # Type of care: "walk", "feeding", "meds", "grooming", etc.
    duration_minutes: int      # How long this task takes to complete
    priority: int              # Scheduling urgency: 1 = low, 2 = medium, 3 = high
    preferred_time: str = ""   # Optional time-of-day hint: "morning", "afternoon", "evening"
    is_completed: bool = False # Tracks whether this task has been done today

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        pass

    def __repr__(self) -> str:
        """Return a readable string representation for display and debugging."""
        pass


# ---------------------------------------------------------------------------
# Pet — the animal being cared for
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str              # Pet's name, e.g. "Buddy"
    species: str           # e.g. "dog", "cat", "rabbit"
    age: int               # Age in years — can influence task needs
    notes: str = ""        # Any medical or behavioral notes about this pet
    tasks: list = field(default_factory=list)  # List of Task objects assigned to this pet
                                               # Uses default_factory to avoid shared state between instances

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        pass

    def get_tasks(self) -> list:
        """Return all tasks associated with this pet."""
        pass


# ---------------------------------------------------------------------------
# Owner — the person with time constraints and preferences
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: dict = None):
        self.name = name                            # Owner's full name
        self.available_minutes = available_minutes  # Total free time available today (in minutes)
        self.preferences = preferences or {}        # Optional preferences, e.g. {"prefer_morning": True}
                                                    # Defaults to empty dict to avoid mutable default argument bug
        self.pets: list[Pet] = []                   # All pets belonging to this owner

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pass

    def get_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        pass


# ---------------------------------------------------------------------------
# Schedule — the planning engine that builds the daily care plan
# ---------------------------------------------------------------------------

class Schedule:
    def __init__(self, owner: Owner, pet: Pet, date: date):
        self.owner = owner                      # Used to apply time and preference constraints
        self.pet = pet                          # Source of tasks to be scheduled
        self.date = date                        # The day this plan is being generated for
        self.planned_tasks: list[Task] = []     # Final ordered list of tasks that fit within constraints
        self.reasoning: list[str] = []          # Human-readable explanation for each scheduling decision

    def generate(self) -> None:
        """Core scheduling logic.

        Sorts pet tasks by priority (high to low), then greedily selects
        tasks that fit within the owner's available_minutes. Records a
        reasoning entry for each task that is included or skipped.
        """
        pass

    def get_total_duration(self) -> int:
        """Return the total time (in minutes) for all planned tasks."""
        pass

    def display_plan(self) -> str:
        """Format the planned tasks and reasoning into a readable string for the UI."""
        pass
