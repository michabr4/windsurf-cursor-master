import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card, CardContent, Grid2, Typography } from "@mui/material";
const cards = [
    { title: "Open Incidents", value: "12" },
    { title: "P1/P2 Active", value: "3" },
    { title: "TAC Cases Open", value: "7" },
    { title: "Device Health Avg", value: "91%" }
];
export function DashboardPage() {
    return (_jsx(Grid2, { container: true, spacing: 2, children: cards.map((card) => (_jsx(Grid2, { size: { xs: 12, sm: 6, md: 3 }, children: _jsx(Card, { children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "subtitle2", children: card.title }), _jsx(Typography, { variant: "h4", children: card.value })] }) }) }, card.title))) }));
}
