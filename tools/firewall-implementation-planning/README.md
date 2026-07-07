# Firewall implementation planning

Starter repository for **MGM** firewall migration work.

## Stakeholder migration summary

- **High-level plan (reduce anxiety, set expectations):** [`docs/MGM_Palo_to_Cisco_Migration_Executive_Plan.md`](docs/MGM_Palo_to_Cisco_Migration_Executive_Plan.md)  
  Derived from the Cisco *FW & SA* proposal, the *PRELIMINARY Project Plan* (DOCX), and the *Palo to Cisco Action Items* (PDF) — *not* a replacement for the formal MOP, CRD, or published PM schedule.

- **Actionable plan (MS Project):** [`project/MGM_Palo_to_Cisco_Actionable_Plan.xml`](project/MGM_Palo_to_Cisco_Actionable_Plan.xml) + Excel import: [`MGM_Palo_to_Cisco_Actionable_Plan_Import.xlsx`](project/MGM_Palo_to_Cisco_Actionable_Plan_Import.xlsx) / [`.xls`](project/MGM_Palo_to_Cisco_Actionable_Plan_Import.xls) — *Import from Excel* in **Project** (see [`project/README_Project_files.md`](project/README_Project_files.md)). *Save As* `*.mpp` after import, or open the **XML** directly in Project.

Add your org-specific runbooks, wave plans, and exports under `docs/` or as your PMO requires.

## Initialize Git (first time on your Mac)

From a Terminal, run:

```bash
cd /Users/michabr4/firewall-implementation-planning
chmod +x setup-git.sh
./setup-git.sh
```

(If a broken `.git` exists from a failed init, the script removes it and starts clean.)

## Connect to GitHub (after `setup-git.sh`)

```bash
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```
