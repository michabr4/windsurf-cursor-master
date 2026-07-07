import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Alert, Box, CircularProgress, Typography } from "@mui/material";
import { factories, models, service } from "powerbi-client";
import { useEffect, useRef, useState } from "react";
import { fetchPowerBiEmbed } from "../api";
const powerbiService = new service.Service(factories.hpmFactory, factories.wpmpFactory, factories.routerFactory);
export function PowerBiPmDashboardPage() {
    const hostRef = useRef(null);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [err, setErr] = useState(null);
    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const res = await fetchPowerBiEmbed();
                if (!cancelled) {
                    setData(res);
                    setErr(null);
                }
            }
            catch (e) {
                if (!cancelled)
                    setErr(e instanceof Error ? e.message : "Failed to load embed");
            }
            finally {
                if (!cancelled)
                    setLoading(false);
            }
        })();
        return () => {
            cancelled = true;
        };
    }, []);
    useEffect(() => {
        if (!data || !("enabled" in data) || data.enabled !== true || !hostRef.current)
            return;
        const el = hostRef.current;
        el.innerHTML = "";
        let embedded = null;
        try {
            embedded = powerbiService.embed(el, {
                type: "report",
                id: data.reportId,
                embedUrl: data.embedUrl,
                accessToken: data.embedToken,
                tokenType: models.TokenType.Embed,
                settings: {
                    panes: {
                        filters: { expanded: false, visible: true },
                        pageNavigation: { visible: true }
                    }
                }
            });
        }
        catch (e) {
            setErr(e instanceof Error ? e.message : "Embed failed");
        }
        return () => {
            if (embedded) {
                try {
                    powerbiService.reset(el);
                }
                catch { /* already disposed */ }
            }
        };
    }, [data]);
    if (loading) {
        return (_jsx(Box, { display: "flex", justifyContent: "center", p: 4, children: _jsx(CircularProgress, {}) }));
    }
    if (err) {
        return _jsx(Alert, { severity: "error", children: err });
    }
    if (!data) {
        return _jsx(Alert, { severity: "warning", children: "No response from embed API." });
    }
    if (!data.enabled) {
        return (_jsx(Alert, { severity: "info", children: data.message ??
                "Power BI is not configured. Set POWERBI_* on the backend (see docs/POWERBI_GLOBAL_PM.md)." }));
    }
    return (_jsxs(Box, { children: [_jsx(Typography, { variant: "h5", gutterBottom: true, children: "Global PM Dashboard" }), _jsxs(Typography, { variant: "body2", color: "text.secondary", sx: { mb: 2 }, children: [data.reportName, " \u00B7 token expires ", data.tokenExpiry] }), _jsx(Box, { ref: hostRef, sx: {
                    minHeight: 720,
                    bgcolor: "#1a1a1a",
                    borderRadius: 1,
                    border: 1,
                    borderColor: "divider",
                    overflow: "hidden"
                } })] }));
}
