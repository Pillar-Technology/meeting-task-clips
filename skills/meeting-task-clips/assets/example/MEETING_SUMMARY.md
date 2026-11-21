# Weekly Product Sync
**Date:** 2026-11-20  
**Participants:** Pak Budi (boss), Rina (staff (designer, the user)), Dion (staff (engineering)), Sari (staff (support / demo))

## 1. Summary (what the bosses need)

Pak Budi wants three things done before the investor demo on 5 December: a three-tier pricing page (Basic, Pro, Enterprise) with monthly and yearly prices, the late verification-email bug in onboarding fixed with a provider comparison if the provider is at fault, and a demo script covering those two flows. The demo will show nothing else. The FAQ update for the new tiers has no owner yet.

**Decisions made:**
- Investor demo on 5 Dec shows only the new pricing page and the fixed onboarding; no new features. *(by Pak Budi, 00:09:30)*

## 2. Task assignments

| # | Task | Assigned to | Assigned by | Deadline | Clip |
|---|------|-------------|-------------|----------|------|
| 1 | Redesign the pricing page with three tiers (Basic, Pro, Enterprise) | Rina | Pak Budi | Friday 28 Nov | [00:01:02–00:05:00](clips/01-task-redesign-the-pricing-page-with-three-tie.mp4) |
| 2 | Investigate the verification-email queue issue and fix it; if the provider is the cause, prepare a comparison of two alternative providers with pricing | Dion | Pak Budi | Fix: ASAP. Provider comparison: Wednesday 26 Nov | [00:06:24–00:09:30](clips/02-task-investigate-the-verification-email-queue.mp4) |
| 3 | Test the verification-email fix once Dion has it ready | Sari | Pak Budi | when the fix is ready | [00:07:48–00:08:35](clips/03-task-test-the-verification-email-fix-once-dio.mp4) |
| 4 | Write the investor demo script covering the pricing page and onboarding flows | Sari | Pak Budi | Draft by Monday 24 Nov | [00:09:40–00:09:50](clips/04-task-write-the-investor-demo-script-covering.mp4) |
| 5 | Update the FAQ page for the new pricing tiers | unassigned (Rina offered, if time allows) | Pak Budi | — | [00:09:50–00:10:04](clips/05-task-update-the-faq-page-for-the-new-pricing.mp4) |

### Task 1: Redesign the pricing page with three tiers (Basic, Pro, Enterprise)
- **Who does it:** Rina
- **Who asked:** Pak Budi
- **Deadline:** Friday 28 Nov
- **What the boss needs (details / acceptance):**
  - Three tiers: Basic (the old single plan), Pro, Enterprise
  - Use the new brand colours from the Figma file Sari shared last week
  - Show monthly and yearly prices, with the yearly discount
  - Free plan is kept but NOT shown on the pricing page; it stays in the signup flow
  - Ready for review before the investor demo
- **Said as:** “Rina, can you redesign the pricing page with the three tiers? Use the new brand colours from the Figma file Sari shared last week, and show both monthly and yearly prices with the yearly discount.”
- **Clip:** `clips/01-task-redesign-the-pricing-page-with-three-tie.mp4` (00:01:02–00:05:00)

### Task 2: Investigate the verification-email queue issue and fix it; if the provider is the cause, prepare a comparison of two alternative providers with pricing
- **Who does it:** Dion
- **Who asked:** Pak Budi
- **Deadline:** Fix: ASAP. Provider comparison: Wednesday 26 Nov
- **What the boss needs (details / acceptance):**
  - Find the root cause of late/missing verification emails (9 of 14 bug reports this week)
  - If the provider is at fault: compare two alternatives including pricing
  - Sari helps with testing once the fix is ready
- **Said as:** “Dion, I need you to look at the email queue this week. Find the root cause, and if it is the provider, get me a comparison of two alternatives with pricing.”
- **Clip:** `clips/02-task-investigate-the-verification-email-queue.mp4` (00:06:24–00:09:30)

### Task 3: Test the verification-email fix once Dion has it ready
- **Who does it:** Sari
- **Who asked:** Pak Budi
- **Deadline:** when the fix is ready
- **What the boss needs (details / acceptance):**
  - Testing support for Dion's fix
- **Said as:** “Yes, Sari helps with testing once the fix is ready.”
- **Clip:** `clips/03-task-test-the-verification-email-fix-once-dio.mp4` (00:07:48–00:08:35)

### Task 4: Write the investor demo script covering the pricing page and onboarding flows
- **Who does it:** Sari
- **Who asked:** Pak Budi
- **Deadline:** Draft by Monday 24 Nov
- **What the boss needs (details / acceptance):**
  - Two flows only: new pricing page and fixed onboarding
  - Send draft to Pak Budi
- **Said as:** “Yes please, Sari, a demo script with the two flows, send me a draft by Monday.”
- **Clip:** `clips/04-task-write-the-investor-demo-script-covering.mp4` (00:09:40–00:09:50)

### Task 5: Update the FAQ page for the new pricing tiers
- **Who does it:** unassigned (Rina offered, if time allows)
- **Who asked:** Pak Budi
- **What the boss needs (details / acceptance):**
  - FAQ must reflect the three tiers
- **Said as:** “And someone needs to update the FAQ page for the new tiers, we'll figure out who later.”
- **Clip:** `clips/05-task-update-the-faq-page-for-the-new-pricing.mp4` (00:09:50–00:10:04)
- **Confidence:** low — Pak Budi said 'we'll figure out who later'; Rina offered conditionally and he replied 'let's see'. Confirm the owner.

## 3. Questions and answers

**Q1 (Rina, 00:02:02):** So we drop the single plan completely?
**A (Pak Budi):** Yes, the single plan becomes Basic.
Clip: `clips/06-qa-so-we-drop-the-single-plan-completely.mp4`

**Q2 (Rina, 00:03:43):** Do we keep the free plan?
**A (Pak Budi):** Keep it, but do not show it on the pricing page; it stays on the signup flow only.
Clip: `clips/07-qa-do-we-keep-the-free-plan.mp4`

**Q3 (Rina, 00:04:25):** When do you need the pricing page?
**A (Pak Budi):** Friday the 28th, to review before the demo.
Clip: `clips/08-qa-when-do-you-need-the-pricing-page.mp4`

**Q4 (Pak Budi, 00:05:00):** How many onboarding bug reports this week?
**A (Sari):** Fourteen; nine are the same late/missing verification email issue.
Clip: `clips/09-qa-how-many-onboarding-bug-reports-this-wee.mp4`

**Q5 (Dion, 00:07:48):** Can I pull Sari in for testing?
**A (Pak Budi):** Yes, once the fix is ready.
Clip: `clips/10-qa-can-i-pull-sari-in-for-testing.mp4`

**Q6 (Dion, 00:08:35):** What is the deadline for the provider comparison?
**A (Pak Budi):** Next Wednesday; the fix itself as soon as possible.
Clip: `clips/11-qa-what-is-the-deadline-for-the-provider-co.mp4`

**Q7 (Sari, 00:09:40):** Should I prepare the demo script?
**A (Pak Budi):** Yes, two flows, draft by Monday.
Clip: `clips/12-qa-should-i-prepare-the-demo-script.mp4`

## 4. Topics, in order (who said what)

### 1. Pricing page: move to three tiers  (00:01:02–00:05:00)
Board agreed on Basic/Pro/Enterprise; Rina redesigns the page by Friday 28.

- **Pak Budi** (00:01:02): Explained the board decision and why the current single-price page confuses customers; assigned the redesign to Rina with brand colours and monthly/yearly prices.
- **Rina** (00:02:02): Asked whether the single plan is dropped (yes, becomes Basic), whether the free plan stays (yes, hidden), and the deadline (Friday 28).

_Related tasks: 1_

### 2. Onboarding: verification email bug  (00:05:00–00:09:30)
14 bug reports, 9 about late/missing verification emails; Dion investigates, Sari tests.

- **Pak Budi** (00:05:00): Asked for the bug count; assigned Dion the root-cause investigation and a provider comparison.
- **Sari** (00:05:37): Reported 14 bug reports, 9 the same email issue; agreed to help test.
- **Dion** (00:07:48): Asked to involve Sari for testing and for the comparison deadline (Wednesday).

_Related tasks: 2, 3_

### 3. Investor demo on 5 December  (00:09:30–00:10:06)
Demo shows only pricing page and onboarding fix; Sari drafts the script by Monday; FAQ owner undecided.

- **Pak Budi** (00:09:30): Decided the demo scope; asked Sari for a script draft; raised the FAQ update without naming an owner.
- **Sari** (00:09:40): Offered to prepare the demo script; accepted the Monday deadline.
- **Rina** (00:09:56): Offered to take the FAQ update if time allows after the pricing page.

_Related tasks: 4, 5_

## 5. Unclear points to confirm

- FAQ page update has no confirmed owner (Rina offered conditionally; Pak Budi said 'let's see').
- Deadline for the email fix is only 'as soon as possible'; no date.
