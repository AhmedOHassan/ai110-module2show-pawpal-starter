import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialisation — runs only on the very first load.
# Think of this as checking the "vault" before putting anything in it.
# If the key already exists, we skip creation so we don't overwrite live data.
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None   # Will hold the Owner object once the form is submitted

if "pet" not in st.session_state:
    st.session_state.pet = None     # Will hold the Pet object once the form is submitted

if "tasks" not in st.session_state:
    st.session_state.tasks = []     # Will hold Task objects added by the user

# ---------------------------------------------------------------------------
# Section 1 — Owner + Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=90)
    prefer_morning = st.checkbox("Prefer morning tasks", value=False)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])

if st.button("Save owner & pet"):
    # Create real objects and store them in the vault so they survive reruns
    owner = Owner(
        name=owner_name,
        available_minutes=int(available_minutes),
        preferences={"prefer_morning": prefer_morning},
    )
    pet = Pet(name=pet_name, species=species, age=0)
    owner.add_pet(pet)

    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.tasks = []
    st.success(f"Saved! Owner: {owner_name} | Pet: {pet_name} ({species})")

# ---------------------------------------------------------------------------
# Section 2 — Task management
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Tasks")

priority_map = {"low": 1, "medium": 2, "high": 3}

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task name", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.selectbox("Preferred time", ["", "morning", "afternoon", "evening"])

if st.button("Add task"):
    if st.session_state.pet is None:
        st.warning("Please save an owner & pet first.")
    else:
        task = Task(
            name=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=priority_map[priority_label],
            preferred_time=preferred_time,
        )
        st.session_state.pet.add_task(task)
        st.session_state.tasks.append(task)
        st.success(f"Added task: {task_title}")

# Display current tasks with Remove + Edit actions
if st.session_state.tasks:
    st.write("Current tasks:")

    # Column headers
    h1, h2, h3, h4, h5 = st.columns([3, 2, 1, 2, 1])
    h1.markdown("**Task**"); h2.markdown("**Duration (min)**")
    h3.markdown("**Priority**"); h4.markdown("**Preferred time**"); h5.markdown("**Action**")

    for i, task in enumerate(st.session_state.tasks):
        c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 2, 1])
        c1.write(task.name); c2.write(task.duration_minutes)
        c3.write(task.priority); c4.write(task.preferred_time or "-")
        if c5.button("Remove", key=f"remove_{i}"):
            st.session_state.pet.remove_task(task)
            st.session_state.tasks.pop(i)
            st.rerun()

    # Edit a task in place
    st.markdown("#### Edit a task")
    task_names = [t.name for t in st.session_state.tasks]
    selected_name = st.selectbox("Select task to edit", task_names, key="edit_select")
    selected_task = next(t for t in st.session_state.tasks if t.name == selected_name)

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        new_name = st.text_input("New name", value=selected_task.name, key="edit_name")
    with e2:
        new_duration = st.number_input("Duration (min)", min_value=1, max_value=240,
                                       value=selected_task.duration_minutes, key="edit_dur")
    with e3:
        new_priority_label = st.selectbox("Priority", ["low", "medium", "high"],
                                          index=selected_task.priority - 1, key="edit_pri")
    with e4:
        time_options = ["", "morning", "afternoon", "evening"]
        time_index = time_options.index(selected_task.preferred_time) if selected_task.preferred_time in time_options else 0
        new_time = st.selectbox("Preferred time", time_options, index=time_index, key="edit_time")

    if st.button("Save edits"):
        # Mutate the Task object directly — it's the same object held by the Pet
        selected_task.name = new_name
        selected_task.duration_minutes = int(new_duration)
        selected_task.priority = priority_map[new_priority_label]
        selected_task.preferred_time = new_time
        st.success(f"Updated: {new_name}")
        st.rerun()

else:
    st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3 — Generate schedule
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None or st.session_state.pet is None:
        st.warning("Please save an owner & pet before generating a schedule.")
    elif not st.session_state.tasks:
        st.warning("Please add at least one task before generating a schedule.")
    else:
        schedule = Schedule(
            owner=st.session_state.owner,
            pets=[st.session_state.pet],
            date=date.today(),
        )
        schedule.generate()

        st.success("Schedule generated!")
        st.markdown(f"**Total planned time:** {schedule.get_total_duration()} / {st.session_state.owner.available_minutes} min")

        st.markdown("### Planned Tasks")
        for i, task in enumerate(schedule.planned_tasks, start=1):
            st.write(f"{i}. {task}")

        st.markdown("### Reasoning")
        for reason in schedule.reasoning:
            st.write(reason)
