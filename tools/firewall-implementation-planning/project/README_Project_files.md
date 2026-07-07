# Microsoft Project files (actionable plan)

## What you have

| File | Purpose |
|------|--------|
| `MGM_Palo_to_Cisco_Actionable_Plan_Import.xlsx` | **Excel 2007+** task sheet + **Import_Instructions** tab. Use **Project** → *Import from Excel* / *New from Excel* (varies by version) and map columns. |
| `MGM_Palo_to_Cisco_Actionable_Plan_Import.xls` | **Excel 97–2003** (`.xls`) with the same **Tasks** data + short **Readme** sheet. Same import flow as the `.xlsx` if your org blocks newer formats. |
| `MGM_Palo_to_Cisco_Actionable_Plan_Task_List.docx` | **Word (readable task list).** Full **task names** in a table, plus WBS, type, duration, predecessor row#s, and notes. Use this if the spreadsheet name column is hard to read. Regenerate: `python3 scripts/project_xml_to_word.py` (see `scripts/requirements-docx.txt`). |
| `MGM_Palo_to_Cisco_Actionable_Plan.xml` | **MS Project XML (MSPDI).** **Open** directly in Project, or *Save As* `*.mpp`. |
| `MGM_Palo_to_Cisco_Actionable_Plan.mpp` | **(Optional)** Build on **Windows** with `Convert-ActionablePlan-ToMpp.ps1` if you have **Project for Windows** and want native `.mpp` from XML. |

**Regenerate Excel** after editing the plan XML:  
`python3 scripts/project_xml_to_excel.py`  
(Requires: `pip install -r scripts/requirements-excel.txt` in a venv.)

**Regenerate the Word task list** (same time as Excel if you changed XML):  
`python3 scripts/project_xml_to_word.py`  
(Requires: `pip install -r scripts/requirements-docx.txt` in a venv.)

> **This Mac / repo cannot embed a true `.mpp` binary** without commercial APIs or a Windows machine with Project. The XML is the portable interchange format; Project creates `.mpp` when you save.

## Rebuild the XML (after changing tasks)

```bash
cd /Users/michabr4/firewall-implementation-planning
python3 scripts/build_actionable_project_xml.py > project/MGM_Palo_to_Cisco_Actionable_Plan.xml
```

## Get `.mpp` on a Mac

1. **Project for Mac (Microsoft 365)**: *File → Open* the XML → *Save As* → `Project` format (`.mpp` / `.mpx2` as offered by your build).  
2. **Or** copy `MGM_Palo_to_Cisco_Actionable_Plan.xml` to a **Windows** PC, run the PowerShell script, or use **Open XML → Save As** in Project.

## Regenerate the script (optional)

Task definitions are in `scripts/build_actionable_project_xml.py` — edit the `R` list, then re-run the command above.
