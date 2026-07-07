import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { Alert, List, ListItem, ListItemText, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { apiGet } from "../api";
export function IncidentsPage() {
    const [incidents, setIncidents] = useState([]);
    const [error, setError] = useState("");
    useEffect(() => {
        apiGet("/incidents")
            .then(setIncidents)
            .catch((e) => setError(e.message));
    }, []);
    return (_jsxs(_Fragment, { children: [_jsx(Typography, { variant: "h5", gutterBottom: true, children: "Incidents" }), error ? _jsx(Alert, { severity: "error", children: error }) : null, _jsx(List, { children: incidents.map((i) => (_jsx(ListItem, { children: _jsx(ListItemText, { primary: `${i.incident_number} - ${i.title}`, secondary: `Priority ${i.priority} | ${i.status}` }) }, i.incident_id))) })] }));
}
