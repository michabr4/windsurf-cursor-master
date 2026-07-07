import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { Alert, List, ListItem, ListItemText, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { apiGet } from "../api";
export function DevicesPage() {
    const [devices, setDevices] = useState([]);
    const [error, setError] = useState("");
    useEffect(() => {
        apiGet("/devices")
            .then(setDevices)
            .catch((e) => setError(e.message));
    }, []);
    return (_jsxs(_Fragment, { children: [_jsx(Typography, { variant: "h5", gutterBottom: true, children: "Devices" }), error ? _jsx(Alert, { severity: "error", children: error }) : null, _jsx(List, { children: devices.map((d) => (_jsx(ListItem, { children: _jsx(ListItemText, { primary: d.hostname, secondary: `${d.ip_address} | ${d.status}` }) }, d.device_id))) })] }));
}
