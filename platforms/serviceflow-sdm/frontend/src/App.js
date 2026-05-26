import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { AppBar, Box, Button, Container, Toolbar, Typography } from "@mui/material";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { IncidentsPage } from "./pages/IncidentsPage";
import { DevicesPage } from "./pages/DevicesPage";
import { PropertiesPage } from "./pages/PropertiesPage";
import { PowerBiPmDashboardPage } from "./pages/PowerBiPmDashboardPage";
import { SalesforcePage } from "./pages/SalesforcePage";
function useSessionToken() {
    const token = localStorage.getItem("accessToken");
    return token;
}
function RequireAuth({ children }) {
    const token = useSessionToken();
    if (!token)
        return _jsx(Navigate, { to: "/login", replace: true });
    return children;
}
export function App() {
    const navigate = useNavigate();
    return (_jsxs(Box, { children: [_jsx(AppBar, { position: "static", children: _jsxs(Toolbar, { children: [_jsx(Typography, { variant: "h6", sx: { flexGrow: 1 }, children: "Service Delivery Manager" }), _jsx(Button, { color: "inherit", onClick: () => navigate("/dashboard"), children: "Dashboard" }), _jsx(Button, { color: "inherit", onClick: () => navigate("/incidents"), children: "Incidents" }), _jsx(Button, { color: "inherit", onClick: () => navigate("/devices"), children: "Devices" }), _jsx(Button, { color: "inherit", onClick: () => navigate("/properties"), children: "Properties" }), _jsx(Button, { color: "inherit", onClick: () => navigate("/powerbi-pm"), children: "Power BI PM" }), _jsx(Button, { color: "inherit", onClick: () => navigate("/salesforce"), children: "Salesforce" }), _jsx(Button, { color: "inherit", onClick: () => {
                                localStorage.removeItem("accessToken");
                                navigate("/login");
                            }, children: "Logout" })] }) }), _jsx(Container, { sx: { mt: 3 }, children: _jsxs(Routes, { children: [_jsx(Route, { path: "/login", element: _jsx(LoginPage, {}) }), _jsx(Route, { path: "/dashboard", element: _jsx(RequireAuth, { children: _jsx(DashboardPage, {}) }) }), _jsx(Route, { path: "/incidents", element: _jsx(RequireAuth, { children: _jsx(IncidentsPage, {}) }) }), _jsx(Route, { path: "/devices", element: _jsx(RequireAuth, { children: _jsx(DevicesPage, {}) }) }), _jsx(Route, { path: "/properties", element: _jsx(RequireAuth, { children: _jsx(PropertiesPage, {}) }) }), _jsx(Route, { path: "/powerbi-pm", element: _jsx(RequireAuth, { children: _jsx(PowerBiPmDashboardPage, {}) }) }), _jsx(Route, { path: "/salesforce", element: _jsx(RequireAuth, { children: _jsx(SalesforcePage, {}) }) }), _jsx(Route, { path: "*", element: _jsx(Navigate, { to: "/dashboard" }) })] }) })] }));
}
