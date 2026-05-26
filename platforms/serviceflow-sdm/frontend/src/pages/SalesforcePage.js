import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Alert, Box, Card, CardContent, Chip, CircularProgress, Grid2, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Tabs, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { apiGet } from "../api";
function fmt(v) {
    if (v === null || v === undefined)
        return "—";
    if (typeof v === "object") {
        const o = v;
        return o.Name ? String(o.Name) : JSON.stringify(v);
    }
    return String(v);
}
function currency(n) {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);
}
function KpiCard({ label, value, sub }) {
    return (_jsx(Card, { children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "subtitle2", color: "text.secondary", children: label }), _jsx(Typography, { variant: "h4", children: value }), sub && _jsx(Typography, { variant: "caption", color: "text.secondary", children: sub })] }) }));
}
export function SalesforcePage() {
    const [tab, setTab] = useState(0);
    const [summary, setSummary] = useState(null);
    const [cases, setCases] = useState(null);
    const [accounts, setAccounts] = useState(null);
    const [opps, setOpps] = useState(null);
    const [entitlements, setEntitlements] = useState(null);
    const [contacts, setContacts] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    useEffect(() => {
        Promise.all([
            apiGet("/salesforce/console-summary"),
            apiGet("/salesforce/cases?limit=50"),
            apiGet("/salesforce/accounts?limit=50"),
            apiGet("/salesforce/opportunities?limit=50"),
            apiGet("/salesforce/entitlements?limit=50"),
            apiGet("/salesforce/contacts?limit=50")
        ])
            .then(([s, c, a, o, e, co]) => {
            setSummary(s);
            setCases(c);
            setAccounts(a);
            setOpps(o);
            setEntitlements(e);
            setContacts(co);
        })
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, []);
    if (loading) {
        return _jsx(Box, { display: "flex", justifyContent: "center", p: 4, children: _jsx(CircularProgress, {}) });
    }
    if (error) {
        return _jsx(Alert, { severity: "error", children: error });
    }
    if (summary && !summary.configured) {
        return (_jsx(Alert, { severity: "info", children: summary.message ?? "Salesforce is not configured. Set SALESFORCE_* environment variables on the backend." }));
    }
    return (_jsxs(Box, { children: [_jsx(Typography, { variant: "h5", gutterBottom: true, children: "Salesforce CRM" }), _jsx(Typography, { variant: "body2", color: "text.secondary", sx: { mb: 2 }, children: "Live Salesforce data powering all SDC program consoles \u2014 Cases, Accounts, Opportunities, Entitlements, and Contacts." }), summary?.pm && (_jsxs(Grid2, { container: true, spacing: 2, sx: { mb: 3 }, children: [_jsx(Grid2, { size: { xs: 12, sm: 6, md: 2.4 }, children: _jsx(KpiCard, { label: "Accounts", value: summary.pm.totalAccounts }) }), _jsx(Grid2, { size: { xs: 12, sm: 6, md: 2.4 }, children: _jsx(KpiCard, { label: "Open Cases", value: summary.delivery?.openCases ?? 0, sub: `${summary.delivery?.highPriorityCases ?? 0} high priority` }) }), _jsx(Grid2, { size: { xs: 12, sm: 6, md: 2.4 }, children: _jsx(KpiCard, { label: "Pipeline", value: currency(summary.pm.pipelineValue), sub: `${summary.pm.activeOpportunities} active` }) }), _jsx(Grid2, { size: { xs: 12, sm: 6, md: 2.4 }, children: _jsx(KpiCard, { label: "Entitlements", value: summary.renewals?.activeEntitlements ?? 0, sub: `${summary.renewals?.expiringIn90Days ?? 0} expiring in 90d` }) }), _jsx(Grid2, { size: { xs: 12, sm: 6, md: 2.4 }, children: _jsx(KpiCard, { label: "Open Tasks", value: summary.pm.openTasks }) })] })), _jsx(Box, { sx: { borderBottom: 1, borderColor: "divider", mb: 2 }, children: _jsxs(Tabs, { value: tab, onChange: (_, v) => setTab(v), children: [_jsx(Tab, { label: "Cases" }), _jsx(Tab, { label: "Accounts" }), _jsx(Tab, { label: "Opportunities" }), _jsx(Tab, { label: "Entitlements" }), _jsx(Tab, { label: "Contacts" })] }) }), tab === 0 && cases && (_jsx(TableContainer, { children: _jsxs(Table, { size: "small", children: [_jsx(TableHead, { children: _jsxs(TableRow, { children: [_jsx(TableCell, { children: "Case #" }), _jsx(TableCell, { children: "Subject" }), _jsx(TableCell, { children: "Status" }), _jsx(TableCell, { children: "Priority" }), _jsx(TableCell, { children: "Account" }), _jsx(TableCell, { children: "Owner" }), _jsx(TableCell, { children: "Created" })] }) }), _jsx(TableBody, { children: cases.records.map((r) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: fmt(r.CaseNumber) }), _jsx(TableCell, { children: fmt(r.Subject) }), _jsx(TableCell, { children: _jsx(Chip, { label: fmt(r.Status), size: "small", color: r.Status === "Closed" ? "default" : "warning" }) }), _jsx(TableCell, { children: fmt(r.Priority) }), _jsx(TableCell, { children: fmt(r.Account) }), _jsx(TableCell, { children: fmt(r.Owner) }), _jsx(TableCell, { children: fmt(r.CreatedDate) })] }, r.Id))) })] }) })), tab === 1 && accounts && (_jsx(TableContainer, { children: _jsxs(Table, { size: "small", children: [_jsx(TableHead, { children: _jsxs(TableRow, { children: [_jsx(TableCell, { children: "Name" }), _jsx(TableCell, { children: "Type" }), _jsx(TableCell, { children: "Industry" }), _jsx(TableCell, { children: "Revenue" }), _jsx(TableCell, { children: "Owner" }), _jsx(TableCell, { children: "City" })] }) }), _jsx(TableBody, { children: accounts.records.map((r) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: fmt(r.Name) }), _jsx(TableCell, { children: fmt(r.Type) }), _jsx(TableCell, { children: fmt(r.Industry) }), _jsx(TableCell, { children: r.AnnualRevenue ? currency(Number(r.AnnualRevenue)) : "—" }), _jsx(TableCell, { children: fmt(r.Owner) }), _jsx(TableCell, { children: fmt(r.BillingCity) })] }, r.Id))) })] }) })), tab === 2 && opps && (_jsx(TableContainer, { children: _jsxs(Table, { size: "small", children: [_jsx(TableHead, { children: _jsxs(TableRow, { children: [_jsx(TableCell, { children: "Name" }), _jsx(TableCell, { children: "Stage" }), _jsx(TableCell, { children: "Amount" }), _jsx(TableCell, { children: "Close Date" }), _jsx(TableCell, { children: "Probability" }), _jsx(TableCell, { children: "Account" }), _jsx(TableCell, { children: "Owner" })] }) }), _jsx(TableBody, { children: opps.records.map((r) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: fmt(r.Name) }), _jsx(TableCell, { children: _jsx(Chip, { label: fmt(r.StageName), size: "small", color: r.StageName === "Closed Won" ? "success" : r.StageName === "Closed Lost" ? "error" : "info" }) }), _jsx(TableCell, { children: r.Amount ? currency(Number(r.Amount)) : "—" }), _jsx(TableCell, { children: fmt(r.CloseDate) }), _jsx(TableCell, { children: r.Probability ? `${r.Probability}%` : "—" }), _jsx(TableCell, { children: fmt(r.Account) }), _jsx(TableCell, { children: fmt(r.Owner) })] }, r.Id))) })] }) })), tab === 3 && entitlements && (_jsx(TableContainer, { children: _jsxs(Table, { size: "small", children: [_jsx(TableHead, { children: _jsxs(TableRow, { children: [_jsx(TableCell, { children: "Name" }), _jsx(TableCell, { children: "Status" }), _jsx(TableCell, { children: "Account" }), _jsx(TableCell, { children: "Start Date" }), _jsx(TableCell, { children: "End Date" }), _jsx(TableCell, { children: "Remaining Cases" })] }) }), _jsx(TableBody, { children: entitlements.records.map((r) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: fmt(r.Name) }), _jsx(TableCell, { children: _jsx(Chip, { label: fmt(r.Status), size: "small", color: r.Status === "Active" ? "success" : "default" }) }), _jsx(TableCell, { children: fmt(r.Account) }), _jsx(TableCell, { children: fmt(r.StartDate) }), _jsx(TableCell, { children: fmt(r.EndDate) }), _jsx(TableCell, { children: fmt(r.RemainingCases) })] }, r.Id))) })] }) })), tab === 4 && contacts && (_jsx(TableContainer, { children: _jsxs(Table, { size: "small", children: [_jsx(TableHead, { children: _jsxs(TableRow, { children: [_jsx(TableCell, { children: "Name" }), _jsx(TableCell, { children: "Email" }), _jsx(TableCell, { children: "Title" }), _jsx(TableCell, { children: "Department" }), _jsx(TableCell, { children: "Account" }), _jsx(TableCell, { children: "Phone" })] }) }), _jsx(TableBody, { children: contacts.records.map((r) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: `${fmt(r.FirstName)} ${fmt(r.LastName)}` }), _jsx(TableCell, { children: fmt(r.Email) }), _jsx(TableCell, { children: fmt(r.Title) }), _jsx(TableCell, { children: fmt(r.Department) }), _jsx(TableCell, { children: fmt(r.Account) }), _jsx(TableCell, { children: fmt(r.Phone) })] }, r.Id))) })] }) }))] }));
}
