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
# Add tasks to Buddy (dog)
# ---------------------------------------------------------------------------

buddy.add_task(Task(
    name="Morning Walk",
    category="walk",
    duration_minutes=30,
    priority=3,
    preferred_time="morning"
))

buddy.add_task(Task(
    name="Breakfast Feeding",
    category="feeding",
    duration_minutes=10,
    priority=3,
    preferred_time="morning"
))

buddy.add_task(Task(
    name="Evening Grooming",
    category="grooming",
    duration_minutes=20,
    priority=1,
    preferred_time="evening"
))

# ---------------------------------------------------------------------------
# Add tasks to Whiskers (cat)
# ---------------------------------------------------------------------------

whiskers.add_task(Task(
    name="Thyroid Medication",
    category="meds",
    duration_minutes=5,
    priority=3,
    preferred_time="morning",
    frequency="daily"
))

whiskers.add_task(Task(
    name="Afternoon Playtime",
    category="enrichment",
    duration_minutes=15,
    priority=2,
    preferred_time="afternoon"
))

# ---------------------------------------------------------------------------
# Build and print today's schedule
# ---------------------------------------------------------------------------

schedule = Schedule(
    owner=owner,
    pets=owner.get_pets(),
    date=date.today()
)

schedule.generate()
print(schedule.display_plan())
