# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- The initial requirements focused on letting a user add one or more pets, create tasks such as walks or feedings, and see plans for today and future days.
- Designed four core classes: `Owner`, `Pet`, `Task`, and `Scheduler`. `Owner` keeps contact info, availability, preferences, and a list of pets. `Pet` stores identity, needs, and default tasks while helping create new task entries. `Task` holds the work item, duration, priority, preferred time, and completion status. `Scheduler` gathers tasks from the owner, applies constraints, orders tasks, and builds the daily plan with explanations.

**b. Design changes**

- Yes. I realized the scheduler needed a stronger tie back to the owner so it always uses that owner’s pets/tasks instead of floating Task lists. I added methods to `Owner`/`Pet` so the scheduler can call `owner.gather_tasks()` and cache those candidates internally. That change let me add pre-filtering logic (day window, max minutes) before sorting tasks and then walk the ranked list sequentially, assigning start minutes so every task in the plan has a concrete why.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- One tradeoff I made is that my scheduler builds the day in a simple linear order (priority first, then next available slot) instead of trying to optimize every possible combination of tasks and time windows. That means it is faster and easier to explain, but it can miss a “perfect” plan in edge cases where a different ordering would fit more tasks.
- I think that tradeoff is reasonable for this scenario because PawPal+ is meant to feel practical and understandable for a busy pet owner. A clear, predictable schedule with explanations is more useful here than a super-complex optimizer that is harder to debug and justify.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
