# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- I started by keeping the model simple and clean: Owner, Pet, Task, and Scheduler.
- Owner holds availability, preferences, and pets. Pet owns tasks. Task stores priority, duration, recurrence, status, and optional scheduled time. Scheduler is the decision engine.
- I wanted the UI layer to stay thin and call scheduler methods instead of duplicating logic in Streamlit.

**b. Design changes**

- I changed the design after the first pass.
- At first, I treated task lists as external inputs, but that felt loose. I moved to owner.gather_tasks so Scheduler always pulls from the source of truth.
- I also added filtering before ranking, then sequential scheduling in a day window. That made behavior easier to test and explain.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- My scheduler considers priority, day window, and max daily minutes.
- It also supports recurring tasks (daily and weekly), status filtering, time sorting, and conflict warnings for overlapping scheduled intervals.
- I prioritized constraints that a real user feels immediately: not enough time in the day, urgent tasks first, and clear warnings when two tasks overlap.

**b. Tradeoffs**

- My main tradeoff was clarity over optimization.
- I used a priority-first, sequential scheduler instead of a heavy optimization algorithm.
- That means it is predictable and explainable, but it may not always find the mathematically best possible arrangement.
- For this project, I think that is the right tradeoff because users need trust and simplicity first.

---

## 3. AI Collaboration

**a. How you used AI**

- I used VS Code Copilot for design iteration, writing tests faster, and tightening edge-case handling.
- The most effective Copilot features for this scheduler were:
	- fast code suggestions while building methods,
	- chat-driven test generation for happy paths and edge cases,
	- quick refactor support when moving logic from UI into Scheduler methods.
- The best prompts were specific and constraint-based, like: add tests for duplicate times, pets with no tasks, unsupported recurrence values, and case-insensitive filters.

**b. Judgment and verification**

- One AI suggestion I rejected as-is was introducing extra complexity in scheduling behavior before core logic was stable.
- I kept the cleaner architecture: Scheduler owns planning logic, app only displays results.
- I evaluated suggestions by checking three things: does this keep design clean, does it match requirements, and do tests prove it.
- I only kept changes that passed pytest and improved readability.

**c. AI strategy reflection**

- Using separate chat sessions for different phases helped a lot.
- I kept one phase focused on system design, one on implementation, one on testing, and one on docs polish.
- That separation stopped context drift and made each session goal-driven.
- My biggest lesson as the lead architect is this: AI is powerful, but I still own the blueprint. I decide boundaries, tradeoffs, and what gets merged. Copilot moves fast, but I set direction and quality bar.

---

## 4. Testing and Verification

**a. What you tested**

- I tested sorting by time, filtering by status and pet name, recurrence behavior, conflict detection, and schedule generation.
- I also tested edge cases like no tasks, exact duplicate start times, unsupported recurrence, and tasks outside the day window.
- These tests mattered because scheduler bugs are usually edge-case bugs, not happy-path bugs.

**b. Confidence**

- I am confident in the current implementation because the core scenarios and key edge cases are covered and passing.
- I would rate reliability at about 4 out of 5 right now.
- Next, I would test more invalid input handling, more recurrence patterns, and richer multi-pet scheduling pressure cases.

---

## 5. Reflection

**a. What went well**

- I am most satisfied with keeping the architecture clean while still shipping features quickly.
- The scheduler methods and test suite now line up, and the UI is using scheduler outputs directly.

**b. What you would improve**

- In another iteration, I would improve task creation in the UI to capture real time windows and recurrence options directly.
- I would also improve README flow so it reads more like a product manual from top to bottom.

**c. Key takeaway**

- My key takeaway is that strong system design still matters more than fast code generation.
- AI can accelerate implementation, but the best results came when I stayed intentional about boundaries, testing, and tradeoffs.
