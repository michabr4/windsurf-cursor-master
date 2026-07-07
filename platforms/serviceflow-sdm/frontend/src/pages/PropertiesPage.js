import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { Alert, List, ListItem, ListItemText, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { apiGet } from "../api";
export function PropertiesPage() {
    const [properties, setProperties] = useState([]);
    const [error, setError] = useState("");
    useEffect(() => {
        apiGet("/properties")
            .then(setProperties)
            .catch((e) => setError(e.message));
    }, []);
    return (_jsxs(_Fragment, { children: [_jsx(Typography, { variant: "h5", gutterBottom: true, children: "Properties" }), error ? _jsx(Alert, { severity: "error", children: error }) : null, _jsx(List, { children: properties.map((p) => (_jsx(ListItem, { children: _jsx(ListItemText, { primary: p.name, secondary: p.property_type }) }, p.property_id))) })] }));
}
