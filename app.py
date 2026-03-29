import streamlit as st

from pawpal_system import (
    Availability,
    Constraints,
    Owner,
    Pet,
    Preferences,
    Priority,
    Scheduler,
    TimeWindow,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name=owner_name,
        contact_email="owner@example.com",
        availability=Availability(day_window=TimeWindow(start_minutes=6 * 60, end_minutes=20 * 60)),
        preferences=Preferences(prefers_morning=False),
    )

owner = st.session_state.owner
if owner.name != owner_name:
    owner.name = owner_name

st.markdown("### Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Pet age", min_value=0, max_value=40, value=2)
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    normalized_name = pet_name.strip()
    if not normalized_name:
        st.warning("Please enter a pet name.")
    elif any(existing_pet.name.lower() == normalized_name.lower() for existing_pet in owner.pets):
        st.warning(f"{normalized_name} is already in your pet list.")
    else:
        owner.add_pet(Pet(name=normalized_name, species=species, age=int(age)))
        st.success(f"Added {normalized_name}.")

if owner.pets:
    st.write("Current pets:")
    st.table([
        {"name": pet.name, "species": pet.species, "age": pet.age}
        for pet in owner.pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Tasks are now created with your Pet class method.")

if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_options = [pet.name for pet in owner.pets]
        selected_pet_name = st.selectbox("Pet", pet_options)
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        pet_lookup = {pet.name: pet for pet in owner.pets}
        target_pet = pet_lookup[selected_pet_name]
        priority_value = {
            "low": Priority.LOW,
            "medium": Priority.MEDIUM,
            "high": Priority.HIGH,
        }[priority_label]
        target_pet.create_task(title=task_title.strip() or "Untitled task", duration=int(duration), priority=priority_value)
        st.success(f"Added task for {target_pet.name}.")

all_tasks = []
for pet in owner.pets:
    for task in pet.default_tasks:
        all_tasks.append(
            {
                "pet": pet.name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority.value,
            }
        )

if all_tasks:
    st.write("Current tasks:")
    st.table(all_tasks)
else:
    st.info("Add at least one pet before creating tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("This now calls your Scheduler logic.")

if st.button("Generate schedule"):
    scheduler = Scheduler(
        owner=owner,
        day_window=owner.availability.day_window,
        constraints=Constraints(max_daily_minutes=owner.preferences.max_daily_minutes),
    )
    plan = scheduler.build_plan(owner)

    if plan.tasks:
        st.success("Schedule generated.")
        st.write("Today's Schedule")
        st.table(
            [
                {
                    "task": task.title,
                    "priority": task.priority.value,
                    "start_minute": task.scheduled_start,
                    "duration_minutes": task.duration_minutes,
                }
                for task in plan.tasks
            ]
        )
        st.write("Why these tasks were chosen:")
        for explanation in plan.explanations:
            st.write(f"- {explanation}")
    else:
        st.info("No schedulable tasks yet. Add tasks and try again.")
