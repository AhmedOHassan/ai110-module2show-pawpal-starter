from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta


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
    frequency: str = "daily"   # How often this task recurs: "daily", "weekly", "as needed"
    is_completed: bool = False # Tracks whether this task has been done today
    pet_name: str = ""         # Back-reference: name of the pet this task belongs to
    due_date: date = field(default_factory=date.today)  # Date this task is due; defaults to today

    def __post_init__(self) -> None:
        """Validate priority on creation to prevent silent scheduling bugs."""
        if not 1 <= self.priority <= 3:
            raise ValueError(f"Priority must be 1, 2, or 3 — got {self.priority}")

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        self.is_completed = True

    def next_occurrence(self) -> Task:
        """Return a new Task due on the next occurrence, or None if frequency is 'as needed'."""
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None     # "as needed" tasks do not auto-recur

        return Task(
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            frequency=self.frequency,
            due_date=next_due,
        )

    def reset(self) -> None:
        """Reset completion status at the start of a new day."""
        self.is_completed = False

    def __repr__(self) -> str:
        """Return a readable string representation for display and debugging."""
        status = "Done" if self.is_completed else "Pending"
        time_hint = f" [{self.preferred_time}]" if self.preferred_time else ""
        return f"{self.name}{time_hint} - {self.duration_minutes} min | Priority {self.priority} | Due {self.due_date} | {status}"


# ---------------------------------------------------------------------------
# Pet — the animal being cared for
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str              # Pet's name, e.g. "Buddy"
    species: str           # e.g. "dog", "cat", "rabbit"
    age: int               # Age in years — can influence task needs
    notes: str = ""        # Any medical or behavioral notes about this pet
    tasks: list = field(default_factory=list)   # List of Task objects assigned to this pet
                                                # Uses default_factory to avoid shared state between instances
    owner: Owner = field(default=None, repr=False)  # Back-reference to the owner of this pet

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list and stamp the pet_name on the task."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> list:
        """Return all tasks associated with this pet."""
        return self.tasks


# ---------------------------------------------------------------------------
# Owner — the person with time constraints and preferences
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: dict = None):
        self.name = name                            # Owner's full name
        self.available_minutes = available_minutes  # Default daily free time (in minutes)
        self.preferences = preferences or {}        # Optional preferences, e.g. {"prefer_morning": True}
                                                    # Defaults to empty dict to avoid mutable default argument bug
        self.pets: list[Pet] = []                   # All pets belonging to this owner

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner and set the back-reference on the pet."""
        pet.owner = self
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def get_all_tasks(self) -> list:
        """Return all tasks across every pet owned by this owner."""
        return [task for pet in self.pets for task in pet.get_tasks()]


# ---------------------------------------------------------------------------
# Schedule — the planning engine that builds the daily care plan
# ---------------------------------------------------------------------------

class Schedule:
    def __init__(self, owner: Owner, pets: list[Pet], date: date, available_minutes: int = None):
        self.owner = owner                          # Used to apply preference constraints
        self.pets = pets                            # List of pets to schedule for (supports multi-pet)
        self.date = date                            # The day this plan is being generated for
        self.available_minutes = (                  # Per-schedule time override; falls back to owner's default
            available_minutes if available_minutes is not None
            else owner.available_minutes
        )
        self.planned_tasks: list[Task] = []         # Final ordered list of tasks that fit within constraints
        self.reasoning: list[str] = []              # Human-readable explanation for each scheduling decision

    def generate(self) -> None:
        """Core scheduling logic.

        Collects tasks from all pets, sorts by priority (high to low), then
        greedily selects tasks that fit within available_minutes. Records a
        reasoning entry for each task that is included or skipped.
        """
        self.planned_tasks = []
        self.reasoning = []
        time_remaining = self.available_minutes

        # Collect all tasks across all pets and sort by priority descending
        all_tasks = [task for pet in self.pets for task in pet.get_tasks()]
        sorted_tasks = sorted(all_tasks, key=lambda t: t.priority, reverse=True)

        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                self.planned_tasks.append(task)
                time_remaining -= task.duration_minutes
                self.reasoning.append(
                    f"[+] '{task.name}' ({task.pet_name}) included - priority {task.priority}, {task.duration_minutes} min"
                )
            else:
                self.reasoning.append(
                    f"[-] '{task.name}' ({task.pet_name}) skipped - needs {task.duration_minutes} min, only {time_remaining} min left"
                )

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and auto-schedule the next occurrence for daily/weekly tasks.

        Returns the newly created Task if one was scheduled, otherwise None.
        """
        task.mark_complete()

        next_task = task.next_occurrence()
        if next_task is None:
            return None

        # Find the pet that owns this task and register the next occurrence
        for pet in self.pets:
            if pet.name == task.pet_name:
                pet.add_task(next_task)
                break

        return next_task

    def detect_conflicts(self) -> list[str]:
        """Return a list of warning strings for planned tasks that share the same time slot."""
        warnings = []

        # Group tasks by their preferred_time slot
        slots: dict[str, list[Task]] = {}
        for task in self.planned_tasks:
            if not task.preferred_time:         # skip tasks with no time slot
                continue
            slots.setdefault(task.preferred_time, []).append(task)

        # Any slot with more than one task is a conflict
        for slot, tasks in slots.items():
            if len(tasks) > 1:
                names = ", ".join(f"'{t.name}' ({t.pet_name})" for t in tasks)
                warnings.append(
                    f"[!] Conflict in {slot} slot: {names} are all scheduled at the same time."
                )

        return warnings

    def reset_all_tasks(self) -> None:
        """Call reset() on every task across all pets to prepare for a new day."""
        for pet in self.pets:
            for task in pet.get_tasks():
                task.reset()

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> list:
        """Return planned_tasks filtered by completion status and/or pet name."""
        return [
            task for task in self.planned_tasks
            if (completed is None or task.is_completed == completed)
            and (pet_name is None or task.pet_name == pet_name)
        ]

    def sort_by_time(self) -> list:
        """Return planned_tasks sorted by preferred_time in HH:MM order, unscheduled tasks last."""
        time_map = {
            "morning":   "08:00",
            "afternoon": "13:00",
            "evening":   "18:00",
            "":          "99:99",   # sentinel - sorts last
        }

        return sorted(
            self.planned_tasks,
            key=lambda task: time_map.get(task.preferred_time, "99:99")
        )

    def get_total_duration(self) -> int:
        """Return the total time (in minutes) for all planned tasks."""
        return sum(task.duration_minutes for task in self.planned_tasks)

    def display_plan(self) -> str:
        """Format the planned tasks and reasoning into a readable string for the UI."""
        lines = [
            f"Today's Schedule - {self.date.strftime('%A, %B %d %Y')}",
            f"Owner: {self.owner.name} | Available time: {self.available_minutes} min",
            "-" * 50,
        ]

        if not self.planned_tasks:
            lines.append("No tasks could be scheduled.")
        else:
            for i, task in enumerate(self.planned_tasks, start=1):
                lines.append(f"  {i}. {task}")

        lines.append("-" * 50)
        lines.append(f"Total time: {self.get_total_duration()} min\n")
        lines.append("Scheduling Reasoning:")
        for reason in self.reasoning:
            lines.append(f"  {reason}")

        return "\n".join(lines)
