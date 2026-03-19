from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule

# ---------------------------------------------------------------------------
# Set up the owner
# ---------------------------------------------------------------------------

owner = Owner(
    name="Sarah",
    available_minutes=90,
    preferences={"prefer_morning": True}
)

# ---------------------------------------------------------------------------
# Create two pets
# ---------------------------------------------------------------------------

buddy = Pet(name="Buddy", species="dog", age=3, notes="Loves long walks")
whiskers = Pet(name="Whiskers", species="cat", age=5, notes="Takes thyroid medication daily")

owner.add_pet(buddy)
owner.add_pet(whiskers)

# ---------------------------------------------------------------------------
# Add tasks OUT OF ORDER (evening first, then afternoon, then morning)
# so sort_by_time() has something meaningful to reorder
# ---------------------------------------------------------------------------

buddy.add_task(Task(
    name="Evening Grooming",
    category="grooming",
    duration_minutes=20,
    priority=1,
    preferred_time="evening"
))

buddy.add_task(Task(
    name="Breakfast Feeding",
    category="feeding",
    duration_minutes=10,
    priority=3,
    preferred_time="morning"
))

buddy.add_task(Task(
    name="Morning Walk",
    category="walk",
    duration_minutes=30,
    priority=3,
    preferred_time="morning"
))

whiskers.add_task(Task(
    name="Afternoon Playtime",
    category="enrichment",
    duration_minutes=15,
    priority=2,
    preferred_time="afternoon"
))

whiskers.add_task(Task(
    name="Thyroid Medication",
    category="meds",
    duration_minutes=5,
    priority=3,
    preferred_time="morning",
    frequency="daily"
))

# Deliberately added at the same evening slot as Buddy's Evening Grooming
# so detect_conflicts() has two separate clashes to report
whiskers.add_task(Task(
    name="Evening Feeding",
    category="feeding",
    duration_minutes=10,
    priority=2,
    preferred_time="evening"
))

# ---------------------------------------------------------------------------
# Build and generate today's schedule
# ---------------------------------------------------------------------------

schedule = Schedule(
    owner=owner,
    pets=owner.get_pets(),
    date=date.today()
)

schedule.generate()
print(schedule.display_plan())

# ---------------------------------------------------------------------------
# detect_conflicts() — warn about same-slot clashes before the day starts
# ---------------------------------------------------------------------------

print("=" * 50)
print("Conflict detection:")
print("=" * 50)
conflicts = schedule.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")

# ---------------------------------------------------------------------------
# sort_by_time() — reorder planned tasks morning → afternoon → evening
# ---------------------------------------------------------------------------

print("=" * 50)
print("Tasks sorted by time of day:")
print("=" * 50)
for i, task in enumerate(schedule.sort_by_time(), start=1):
    print(f"  {i}. {task}")

# ---------------------------------------------------------------------------
# filter_tasks() — pending tasks only
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("Pending tasks only:")
print("=" * 50)
pending = schedule.filter_tasks(completed=False)
for task in pending:
    print(f"  - {task}")

# ---------------------------------------------------------------------------
# filter_tasks() — Buddy's tasks only
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("Buddy's tasks only:")
print("=" * 50)
for task in schedule.filter_tasks(pet_name="Buddy"):
    print(f"  - {task}")

# ---------------------------------------------------------------------------
# filter_tasks() — Whiskers's tasks only
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("Whiskers's tasks only:")
print("=" * 50)
for task in schedule.filter_tasks(pet_name="Whiskers"):
    print(f"  - {task}")

# ---------------------------------------------------------------------------
# Mark one task complete, then filter for completed tasks
# ---------------------------------------------------------------------------

schedule.complete_task(schedule.planned_tasks[0])   # mark the first planned task done

print()
print("=" * 50)
print("Completed tasks:")
print("=" * 50)
completed = schedule.filter_tasks(completed=True)
if completed:
    for task in completed:
        print(f"  - {task}")
else:
    print("  None yet.")
