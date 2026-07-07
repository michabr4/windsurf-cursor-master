#!/usr/bin/env python3
"""Build MSPDI XML for MGM actionable firewall plan. Run: python3 build_actionable_project_xml.py > ../project/MGM_Palo_to_Cisco_Actionable_Plan.xml"""
from __future__ import annotations

import sys
from xml.sax.saxutils import escape

NS = "http://schemas.microsoft.com/project"
START = "2026-04-28T08:00:00"  # Monday anchor; adjust in Project after open


def dur_h(days: float) -> str:
    return f"PT{int(round(days * 8))}H0M0S"


def main() -> None:
    # (id, wbs, outline, name, summary, milestone, days, preds, notes)
    R: list[tuple] = []
    R.append(
        (0, "0", 0, "MGM Palo to Cisco: Actionable program (working plan)", 1, 0, 0.0, [], "Synthesizes action log + executive plan. Baseline with Cisco PM/Ops.")
    )
    # A — discovery
    R.append((1, "1", 1, "A. Technical discovery & readiness", 1, 0, 0.0, [], ""))
    rows = [
        ("1.1", 2, "SCC: MGM access, demo/ordering, activation", 3, []),
        ("1.2", 2, "VPN: crypto alignment + ~19-tunnel review (owners assigned)", 5, []),
        ("1.3", 2, "Joint: critical app list + validation test plan", 5, []),
        ("1.4", 2, "Site survey firewall priority to Technologent (update w/ FMT)", 2, []),
        ("1.5", 2, "Complete low-level diagrams for in-scope firewalls", 5, []),
        ("1.6", 2, "Assemble program documentation (e.g. Jason, Mani)", 3, []),
        ("1.7", 2, "Second weekly technical call + name net/sec participants", 2, []),
        ("1.8", 2, "NetScout TAPs: align w/ PM/BU/field (e.g. Phil Miller, Srikanth)", 4, []),
        ("1.9", 2, "Run exports through FMT; document gaps/risks", 10, []),
        ("1.10", 2, "Schedule basic FTD/FMC operations training", 2, []),
        ("1.11", 2, "Credential prep list + handoff per MGM policy (AD, TACACS, etc.)", 2, []),
        ("1.12", 2, "Pre/post check scripts: sessions, latency, owners (Cisco+MGM agreed)", 3, []),
        ("1.13", 2, "Clarify User-ID / AD / VM (regionals, LV data centers)", 3, []),
        ("1.14", 2, "Mandalay Bay: validate site-survey data completeness w/ Technologent", 2, []),
        ("1.15", 2, "Propose + approve migrations per week (ops capacity / CAB)", 3, []),
        ("1.16", 2, "FMC: v10/upgrade path, mgmt IP for 4600s, Nexar/hostname inputs", 5, []),
        ("1.17", 2, "Begin AD + RADIUS integration in lab/FMC (early, where possible)", 8, []),
        ("1.18", 2, "Send VM integration document pack to Mo Baker / cyber", 2, []),
        ("1.19", 2, "AD + RADIUS sessions — calendar and required attendees", 2, []),
        ("1.20", 2, "Log/SIEM ingestion path — align w/ Ryan Palmer / security", 4, []),
        ("1.21", 2, "Define export/refresh of XML for migration test cycles", 2, []),
        ("1.22", 2, "SCC: test account with FMC, confirm product/license activation", 2, []),
        ("1.23", 2, "Threat intel: session w/ Jose (licensing, integrations)", 1, []),
        ("1.24", 2, "Palo lab review — nuances feeding MOP/CRD", 5, []),
        ("1.25", 2, "Top parallel task list w/ program lead (pick-up items)", 2, []),
        ("1.26", 2, "CRD: draft, route, approve (governance record)", 3, []),
    ]
    uid = 2
    for wbs, ol, name, dd, _ in rows:
        R.append((uid, wbs, ol, name, 0, 0, float(dd), [1], ""))
        uid += 1
    # Gate after FMT(1.9 uid 10), app(1.3 uid4), crd(1.26=uid?) 
    # uids: 0 summary,1 phA, 2..27 are 1.1..1.26 -> 1.9 is uid=10, 1.3 is uid=4, 1.26 is uid=27
    gate = uid
    R.append(
        (gate, "1.27", 2, "GATE: Discovery + FMT + app plan + CRD (pilot go)", 0, 1, 0.0, [10, 4, 27, 1], "Adjust predecessors in Project if your IDs differ.")
    )
    uid = gate + 1
    b = uid
    R.append((b, "2", 1, "B. Engineering, MOP, and physical handoffs", 1, 0, 0.0, [], "Overlaps late discovery; tracks execution from action list."))
    uid += 1
    b1, b2, b3, b4 = uid, uid + 1, uid + 2, uid + 3
    R.append(
        (b1, "2.1", 2, "Apply lab upgrades + clean AD/realm/RADIUS in FMC/FTD build", 0, 0, 5.0, [b, gate, 18], "UID 18 = early AD/RADIUS in lab (1.17).")
    )
    R.append(
        (b2, "2.2", 2, "Publish MOP, rollback, VPN 420/421 in SharePoint", 0, 0, 4.0, [b, 10, 4, gate], "UIDs 10=FMT (1.9), 4=critical apps (1.3).")
    )
    R.append(
        (b3, "2.3", 2, "Technologent: rack/position + site survey outputs to Nexar/hostname", 0, 0, 3.0, [b, 15, 1], "UID 15 = Mandalay survey validation (1.14).")
    )
    R.append(
        (b4, "2.4", 2, "GATE: MOP + physical/hostname data ready to schedule pilot", 0, 1, 0.0, [b1, b2, b3, gate], "")
    )
    uid = b4 + 1
    c = uid
    R.append((c, "3", 1, "C. Pilot (first in-scope property name TBD)", 1, 0, 0.0, [], ""))
    uid += 1
    c1, c2, c3, c4, c5, c6 = uid, uid + 1, uid + 2, uid + 3, uid + 4, uid + 5
    R.append(
        (c1, "3.1", 2, "Validate L1/L2, register to FMC, load migration build", 0, 0, 5.0, [c, b4, 1], "Per PRELIMINARY plan: physical + registration first.")
    )
    R.append((c2, "3.2", 2, "5–10 day config freeze + comms to stakeholders", 0, 0, 7.0, [c1], "No ad-hoc PA changes; refresh exports before freeze as needed."))
    R.append(
        (c3, "3.3", 2, "During freeze: FMT/parity, manual fix, signed readiness for window", 0, 0, 7.0, [c2, 10], "UID 10 = FMT (1.9).")
    )
    R.append(
        (c4, "3.4", 2, "Migration window: execute MOP, apps on-call, validate", 0, 0, 2.0, [c3, b2, gate], "Replace with formal MOP; gate = discovery/CRD.")
    )
    R.append((c5, "3.5", 2, "Stabilize + high-touch, failover test, hotwash", 0, 0, 5.0, [c4], ""))
    R.append(
        (c6, "3.6", 2, "GATE: pilot approved to begin waves", 0, 1, 0.0, [c5, gate, 4], "4 = 1.3 app plan; prove pilot success before scale")
    )
    uid = c6 + 1
    d = uid
    R.append((d, "4", 1, "D. Program waves to finish the estate", 1, 0, 0.0, [], ""))
    uid += 1
    d1, d2, d3 = uid, uid + 1, uid + 2
    R.append(
        (d1, "4.1", 2, "Wave schedule + resourcing: Cisco, Technologent, MGM, apps", 0, 0, 5.0, [d, 16, c6], "16 = 1.15 (migrations/week) — edit as needed")
    )
    R.append(
        (d2, "4.2", 2, "Execute remaining CAB windows / sites (placeholder length)", 0, 0, 60.0, [d1, c6], "Tie to approved calendar; 60d is placeholder only.")
    )
    R.append((d3, "4.3", 2, "GATE: migration complete — Palo decommissioned in scope", 0, 1, 0.0, [d2, 1], "Commercial true-down follows contract."))
    uid = d3 + 1
    e = uid
    R.append((e, "5", 1, "E. Program close, KT, lifecycle (Day-2)", 1, 0, 0.0, [], ""))
    uid += 1
    e1, e2 = uid, uid + 1
    R.append(
        (e1, "5.1", 2, "As-builts, handover, lifecycle adoption touchpoints", 0, 0, 10.0, [e, d3], "Training + runbooks; SIEM/ops as agreed")
    )
    R.append(
        (e2, "5.2", 2, "GATE: program close / benefits", 0, 1, 0.0, [e1], "")
    )
    out = [emit_header(R, START), "  <Tasks>"]
    for row_id, t in enumerate(R):
        uid, wbs, ol, name, sm, ms, ddays, preds, note = t
        on = "0" if row_id == 0 else t[1]
        out.append(
            task_block(
                row_id, uid, wbs, on, ol, name, sm, ms, ddays, preds, note, START
            )
        )
    out.append("  </Tasks>")
    out.append("\n  <Resources>")
    for i, n in enumerate(
        [
            "MGM program lead",
            "Cisco (PM/engineering)",
            "Technologent (physical)",
            "MGM net/sec/ops",
            "MGM apps/owners",
            "MGM cyber/SOC",
        ]
    ):
        out.append(
            f'    <Resource><UID>{i}</UID><ID>{i}</ID><Name>{escape(n)}</Name><Type>1</Type><IsNull>0</IsNull></Resource>'
        )
    out.append("  </Resources>\n  <Assignments></Assignments>\n</Project>")
    text = "\n".join(out)
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


def emit_header(_rows, start: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Project xmlns="{NS}">
  <SaveVersion>14</SaveVersion>
  <UID>0</UID>
  <Name>MGM_Palo_to_Cisco_Actionable_Plan</Name>
  <Title>MGM: Palo to Cisco — Actionable migration plan (working)</Title>
  <ScheduleFromStart>1</ScheduleFromStart>
  <StartDate>{start}</StartDate>
  <CurrentDate>{start}</CurrentDate>
  <CalendarUID>1</CalendarUID>
  <DefaultStartTime>08:00:00</DefaultStartTime>
  <DefaultFinishTime>17:00:00</DefaultFinishTime>
  <MinutesPerDay>480</MinutesPerDay>
  <MinutesPerWeek>2400</MinutesPerWeek>
  <DaysPerMonth>20</DaysPerMonth>
  <NewTasksAreManual>0</NewTasksAreManual>
  <Calendars>
    <Calendar>
      <UID>1</UID>
      <Name>Standard</Name>
      <IsBaseCalendar>1</IsBaseCalendar>
      <BaseCalendarUID>-1</BaseCalendarUID>
      <WeekDays>
        <WeekDay><DayType>1</DayType><DayWorking>0</DayWorking></WeekDay>
        <WeekDay><DayType>2</DayType><DayWorking>1</DayWorking>
          <WorkingTimes>
            <WorkingTime><FromTime>08:00:00</FromTime><ToTime>12:00:00</ToTime></WorkingTime>
            <WorkingTime><FromTime>13:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime>
          </WorkingTimes>
        </WeekDay>
        <WeekDay><DayType>3</DayType><DayWorking>1</DayWorking>
          <WorkingTimes>
            <WorkingTime><FromTime>08:00:00</FromTime><ToTime>12:00:00</ToTime></WorkingTime>
            <WorkingTime><FromTime>13:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime>
          </WorkingTimes>
        </WeekDay>
        <WeekDay><DayType>4</DayType><DayWorking>1</DayWorking>
          <WorkingTimes>
            <WorkingTime><FromTime>08:00:00</FromTime><ToTime>12:00:00</ToTime></WorkingTime>
            <WorkingTime><FromTime>13:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime>
          </WorkingTimes>
        </WeekDay>
        <WeekDay><DayType>5</DayType><DayWorking>1</DayWorking>
          <WorkingTimes>
            <WorkingTime><FromTime>08:00:00</FromTime><ToTime>12:00:00</ToTime></WorkingTime>
            <WorkingTime><FromTime>13:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime>
          </WorkingTimes>
        </WeekDay>
        <WeekDay><DayType>6</DayType><DayWorking>1</DayWorking>
          <WorkingTimes>
            <WorkingTime><FromTime>08:00:00</FromTime><ToTime>12:00:00</ToTime></WorkingTime>
            <WorkingTime><FromTime>13:00:00</FromTime><ToTime>17:00:00</ToTime></WorkingTime>
          </WorkingTimes>
        </WeekDay>
        <WeekDay><DayType>7</DayType><DayWorking>0</DayWorking></WeekDay>
      </WeekDays>
    </Calendar>
  </Calendars>"""


def task_block(row_id, uid, wbs, outline_n, ol, name, sm, ms, ddays, preds, note, start) -> str:
    dur = "PT0H0M0S" if ddays == 0 and ms else (dur_h(ddays) if ddays else "PT0H0M0S")
    if ms and ddays == 0:
        dur = "PT0H0M0S"
    plines = []
    for p in preds:
        plines.append(
            "      <PredecessorLink><PredecessorUID>%d</PredecessorUID><Type>1</Type><CrossProject>0</CrossProject><LinkLag>0</LinkLag><LagFormat>7</LagFormat></PredecessorLink>"
            % p
        )
    pred_block = "\n" + "\n".join(plines) + "\n" if plines else ""
    ntxt = f"      <Notes>{escape(note)}</Notes>\n" if note else ""
    return f"""    <Task>
      <UID>{uid}</UID>
      <ID>{row_id}</ID>
      <Name>{escape(name)}</Name>
      <Active>1</Active>
      <Manual>0</Manual>
      <Type>0</Type>
      <IsNull>0</IsNull>
      <WBS>{wbs}</WBS>
      <OutlineNumber>{outline_n}</OutlineNumber>
      <OutlineLevel>{ol}</OutlineLevel>
      <Priority>500</Priority>
      <Summary>{"1" if sm else 0}</Summary>
      <Critical>0</Critical>
      <Milestone>{"1" if ms else 0}</Milestone>
      <Duration>{dur}</Duration>
      <DurationFormat>7</DurationFormat>
      <Start>{start}</Start>
      <Finish>{start}</Finish>
      <CalendarUID>1</CalendarUID>
{pred_block}{ntxt}    </Task>"""


if __name__ == "__main__":
    main()
