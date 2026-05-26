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

function RequireAuth({ children }: { children: JSX.Element }) {
  const token = useSessionToken();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export function App() {
  const navigate = useNavigate();

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Service Delivery Manager
          </Typography>
          <Button color="inherit" onClick={() => navigate("/dashboard")}>Dashboard</Button>
          <Button color="inherit" onClick={() => navigate("/incidents")}>Incidents</Button>
          <Button color="inherit" onClick={() => navigate("/devices")}>Devices</Button>
          <Button color="inherit" onClick={() => navigate("/properties")}>Properties</Button>
          <Button color="inherit" onClick={() => navigate("/powerbi-pm")}>Power BI PM</Button>
          <Button color="inherit" onClick={() => navigate("/salesforce")}>Salesforce</Button>
          <Button
            color="inherit"
            onClick={() => {
              localStorage.removeItem("accessToken");
              navigate("/login");
            }}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 3 }}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<RequireAuth><DashboardPage /></RequireAuth>} />
          <Route path="/incidents" element={<RequireAuth><IncidentsPage /></RequireAuth>} />
          <Route path="/devices" element={<RequireAuth><DevicesPage /></RequireAuth>} />
          <Route path="/properties" element={<RequireAuth><PropertiesPage /></RequireAuth>} />
          <Route path="/powerbi-pm" element={<RequireAuth><PowerBiPmDashboardPage /></RequireAuth>} />
          <Route path="/salesforce" element={<RequireAuth><SalesforcePage /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Container>
    </Box>
  );
}
