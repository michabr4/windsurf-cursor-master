# MGM Resorts - Status Report
**Period:** March 10 - April 10, 2026  
**Generated:** April 10, 2026  
**Source:** Webex Spacelift Export Analysis

---

## Executive Summary

MGM engagement is at a **critical inflection point** with the Palo Alto firewall migration deal nearing PO finalization. Multiple workstreams are active across ISE automation, LCS support, and the major Firepower migration initiative. Key risk: **Palo Alto support expires April 15th** with no third-party coverage confirmed.

### Overall Status: 🟡 YELLOW
- Firewall migration PO pending MGM internal review
- Palo Alto support gap after April 15th unresolved
- Technical discovery starting April 10th
- ISE automation progressing with minor issues

---

## Active Workstreams

### 1. Firepower Migration (HIGH PRIORITY)
**Space:** MGM Firepower War Room (181 messages), MGM Firepower Delivery (22 messages)

#### Status
- **Deal Status:** SO/Contract documents sent to MGM (April 7) - awaiting PO
- **Technical Kickoff:** Scheduled for April 10 - core technical discovery
- **Plan Target:** 1-1.5 weeks to complete plan buildout
- **Network Access:** Being provisioned for delivery team (Daniel, Mike Culp, Alberto)

#### Key Updates
| Date | Update |
|------|--------|
| 04/09 | Solid technical agenda ready for MGM; getting network/admin access to SCC |
| 04/08 | Paul Snow at MGM - PAN offered "massive" service extension, MGM declined (reinforces Cisco partnership) |
| 04/07 | All FW and Secure Access docs sent to MGM for review |
| 04/06 | Mike Culp flagged S2S VPN migration complexity - needs PAN license extension |

#### Critical Risk: Palo Alto Support Gap
- **Deadline:** April 15, 2026 - PAN support expires
- **Status:** No third-party support coverage confirmed
- **Mitigation Strategy:**
  - Relying on internal Cisco teams with PAN experience
  - Mike Culp allocation increasing to 75-80%
  - "Frying Pan" space created with Cisco PAN experts (ex-PAN employees)
  - Technologent resources available but not PAN experts

#### Action Items
- [ ] Daniel Molina - Test SCC access ASAP (email sent 04/10)
- [ ] Identify Nexar's 3rd party support group (Phil investigating)
- [ ] Get MGM security team involved with Nexar on access/training
- [ ] Finalize Mike Culp allocation increase (Jason Maz/Jason Am working with Joe)
- [ ] Schedule Netscout TAPs call with Phil Miller (Scott Frisby)

#### Key Personnel
- **Mike Brown (michabr4)** - Delivery Lead
- **Jason Anderson (jasoand2)** - CX Leadership
- **Paul Snow (psnow)** - Sales Lead (on-site at MGM)
- **Mike Culp (miculp)** - Technical Lead (Firepower)
- **Scott Frisby (sfrisby)** - Delivery
- **Nicholas Carrie (nicarrie)** - Engineering
- **Debbie Kennedy (debkenne)** - Support Coordination

---

### 2. ISE as Code Adoption (ISAAC)
**Space:** MGM Digitized Delivery - ISE as Code Adoption (54 messages)

#### Status
- **Certificate Playbook:** Running successfully on all nodes except PSN05
- **PSN05 Issue:** Error encountered - Naga sending logs for investigation
- **Goal:** Use ISAAC for upcoming ISE Patch 10 upgrade in production

#### Recent Progress
| Date | Update |
|------|--------|
| 04/09 | Certificate playbook running, renewal in progress |
| 04/09 | Installation completed on all nodes except PSN05 |
| 03/30 | Target set: ISE Patch 10 upgrade via ISAAC to demonstrate ROI |

#### Action Items
- [ ] Investigate PSN05 error (Naga to send logs)
- [ ] Complete certificate renewal across deployment
- [ ] Prepare for ISE Patch 10 upgrade demonstration

---

### 3. LCS - R&S Support
**Space:** MGM LCS - R&S - Syslog Analysis, SIAR, PSIRT, FN, PSSR (81 messages)

#### Status
- **Team:** Rakesh Gade back in office (04/08)
- **Active Monitoring:** Syslog analysis, PSIRT, Field Notices

#### Recent Issues
| Date | Issue | Status |
|------|-------|--------|
| 04/07 | New syslog 'PMAN-0-PROCFAILCRIT' on Catalyst 3K at Northfield | Monitoring - ~10 devices, recommendation to reload |

#### Action Items
- [ ] Monitor PMAN-0-PROCFAILCRIT syslog on Catalyst 3K devices
- [ ] Follow up with Nitin on Northfield site issues

---

### 4. CX Delivery Leadership
**Space:** MGM CX Delivery & Success Leadership (INT) (121 messages)

#### Key Decisions
- **Onsite Resource:** Confirmed NO Cisco onsite resource available (Jason AM)
- **Resource Strategy:** Increase Mike Culp to 75-80% allocation
- **PAN Support:** Internal teams + Cisco PAN experts (Frying Pan space)

---

## Timeline of Critical Events

```
Mar 26  - Firewall deal momentum building
Mar 30  - Deal valued ~$10M (FW + potential Secure Access/Zscaler takeout)
Mar 31  - Pre-sales kickoff with MGM; Mike Culp onboarding started
Apr 02  - Internal coordination on customer communications
Apr 03  - Firewall Migration Priority list shared
Apr 06  - S2S VPN complexity flagged; PAN support gap identified
Apr 07  - SO/Contract docs sent to MGM
Apr 08  - Paul Snow on-site at MGM; PAN "scorched earth" offer declined
Apr 09  - Technical agenda finalized; PO pending internal review
Apr 10  - Technical discovery kickoff scheduled
Apr 15  - ⚠️ DEADLINE: Palo Alto support expires
```

---

## Risk Register

| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| PAN support expires Apr 15 with no coverage | **HIGH** | Internal PAN experts, Culp allocation increase | Jason Anderson |
| S2S VPN migration complexity | **MEDIUM** | Early identification, may need PAN license extension | Mike Culp |
| PSN05 certificate error | **LOW** | Investigation in progress | Rakesh Gade |
| Resource constraints | **MEDIUM** | Culp to 75-80%, Frying Pan expert group | Jason Maz |

---

## Next Steps (Immediate)

1. **April 10:** Technical discovery call with MGM - core technical deep dive
2. **April 10:** Daniel to validate SCC access
3. **This Week:** Complete plan buildout (1-1.5 week target)
4. **Before April 15:** Finalize PAN support gap mitigation strategy
5. **Ongoing:** Monitor PO status - allow MGM space for internal review

---

## Stakeholder Communications

### Internal
- Daily standups with delivery team
- Weekly escalation meetings with engineering
- "Frying Pan" space for PAN technical support

### External (MGM)
- Phil Miller - Primary technical contact
- Jim Kimball - Executive sponsor
- Security team engagement needed for Nexar access/training

---

*Report compiled from Webex Spacelift export analysis*
