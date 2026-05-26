import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Alert, Box, Button, Stack, TextField, Typography } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";
export function LoginPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState(import.meta.env.DEV ? "admin@serviceflow.local" : "");
    const [password, setPassword] = useState(import.meta.env.DEV ? "ChangeMe123!" : "");
    const [error, setError] = useState("");
    return (_jsxs(Stack, { spacing: 2, sx: { maxWidth: 420, mt: 6 }, children: [_jsx(Typography, { variant: "h5", children: "Login" }), _jsxs(Typography, { variant: "body2", color: "text.secondary", children: ["This dev app uses its own browser storage. To use mockup ", _jsx("strong", { children: "Live data" }), " at", " ", _jsx("code", { children: "/mockup/" }), ", sign in again on the Operations page at", " ", _jsx("code", { children: "http://localhost:3000/" }), " (same JWT is not shared across ports)."] }), error ? _jsx(Alert, { severity: "error", children: error }) : null, _jsx(TextField, { label: "Email", value: email, onChange: (e) => setEmail(e.target.value) }), _jsx(TextField, { label: "Password", type: "password", value: password, onChange: (e) => setPassword(e.target.value) }), _jsx(Box, { children: _jsx(Button, { variant: "contained", onClick: async () => {
                        try {
                            await login(email, password);
                            navigate("/dashboard");
                        }
                        catch (e) {
                            setError(e.message);
                        }
                    }, children: "Sign in" }) })] }));
}
