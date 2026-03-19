from pawpal_system import Task, Pet


# ---------------------------------------------------------------------------
# Test 1: Task Completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should flip is_completed from False to True."""
    task = Task(name="Morning Walk", category="walk", duration_minutes=30, priority=3)

    # Task should start as not completed
    assert task.is_completed is False

    task.mark_complete()

    # Task should now be marked as done
    assert task.is_completed is True


# ---------------------------------------------------------------------------
# Test 2: Task Addition
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Buddy", species="dog", age=3)

    # Pet starts with no tasks
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task(name="Breakfast Feeding", category="feeding", duration_minutes=10, priority=3))

    # Pet should now have exactly one task
    assert len(pet.get_tasks()) == 1
