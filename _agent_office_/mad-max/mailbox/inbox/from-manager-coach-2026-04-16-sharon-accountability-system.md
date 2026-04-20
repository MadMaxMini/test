# From: Manager Coach
# To: Mad Max
# Date: 2026-04-16
# Re: Sharon Accountability + Auto-Payroll System — Build Request
# Priority: High

## Context

Sharon is a part-time ops person for Dakota & LLC (family real estate biz). $400/month, ~10 hrs/week (~2 hrs/day). Flexible schedule — she can skip days as long as she communicates. The problem: she goes dark for days, no comms, no work, no explanation. Then guilt-skips her own payroll, which also delays Tram's pay (Sharon runs payroll for both).

Rod does NOT want hour tracking or timesheets. The model is flipped: **default = she's working. She only reports when she's NOT.**

## What Rod Wants Built

### 1. Daily Activity Check (the "tattler")
- End of each business day (CT), check for Sharon activity:
  - Git commits in `~/Work/dakota-ops/` (her repo)
  - Any communication to Rod or Doc (text detection TBD — may just be commit-based initially)
- **If no activity AND no communication from Sharon that day:**
  - Log it as a "missed day" (silent, no comms, no work)
  - Send Sharon a daily text/notification: "No activity or communication detected today — this counts as a missed day."
  - She gets the message same day, every time. No surprises.

### 2. Monthly Payroll Summary (auto-generated)
- End of month, generate a summary:
  - Total working days in month
  - Days with activity (commits)
  - Days with communication but no commits (excused — she said she wasn't working)
  - Days with no activity AND no communication (dings)
  - **Pay calculation:** $400 - ($20 x missed days) = month's pay
- Send to Sharon: "Sharon, your pay this month: $X. Here's the breakdown: [log]"
- She then processes payroll for herself AND Tram based on this
- Tram's pay is NOT affected by Sharon's dings — Tram gets paid on schedule regardless

### 3. Payroll Separation
- Sharon runs payroll (that's part of her job — Rod wants her doing this)
- But Tram's pay runs on schedule no matter what. Sharon cannot hold Tram's pay hostage to her own guilt cycle.
- System should flag if Tram hasn't been paid by expected date

## Key Design Principles
- No hour tracking, no timesheets, no approval layers
- Default = she's working. Burden is on her to communicate absences.
- The system is transparent — she sees the same data Rod sees
- Daily feedback loop so nothing builds up silently
- Consequence is automatic and mathematical, not emotional
- Rod stays OUT of the chase loop — the system does the talking

## Relevant Paths
- Dakota-ops repo: `~/Work/dakota-ops/`
- Sharon's tasks: `~/Work/dakota-ops/people/sharon/tasks.md`
- Sharon's profile: `claude-life/_agent_office_/people/real-estate/sharon.md`

## Notes
- Comms channel for the daily text TBD — could be Signal, iMessage, or a bot. Rod to decide.
- Git commit tracking is the simplest starting point. Layer on more signals later.
- This ties into the broader Airbnb automation work — as more gets automated, the system tracks more.
