import React from 'react';
import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Toolbar,
  Divider,
  Chip,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BusinessIcon from '@mui/icons-material/Business';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import DeviceHubIcon from '@mui/icons-material/DeviceHub';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';
import { useLocation, useNavigate } from 'react-router-dom';

interface SidebarProps {
  drawerWidth: number;
  mobileOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Properties', path: '/properties', icon: <BusinessIcon /> },
  { label: 'Incidents', path: '/incidents', icon: <WarningAmberIcon /> },
  { label: 'TAC Cases', path: '/tac', icon: <SupportAgentIcon /> },
  { label: 'Technologies', path: '/technologies', icon: <DeviceHubIcon /> },
  { label: 'Licenses', path: '/licenses', icon: <VpnKeyIcon /> },
  { label: 'Reports', path: '/reports', icon: <AssessmentIcon /> },
];

const bottomItems = [
  { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
];

const DrawerContent: React.FC<{ onNavigate: (path: string) => void; currentPath: string }> = ({
  onNavigate,
  currentPath,
}) => (
  <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
    <Toolbar sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2 }}>
      <Box
        sx={{
          width: 32,
          height: 32,
          borderRadius: 1,
          bgcolor: 'primary.main',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, fontSize: 12 }}>
          SF
        </Typography>
      </Box>
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
          ServiceFlow
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1 }}>
          SDM Platform
        </Typography>
      </Box>
    </Toolbar>

    <Divider />

    <Box sx={{ px: 1.5, py: 1 }}>
      <Typography variant="caption" color="text.secondary" sx={{ px: 1, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
        MGM GES-West
      </Typography>
    </Box>

    <List dense sx={{ flexGrow: 1, px: 1 }}>
      {navItems.map((item) => {
        const active = currentPath === item.path || (item.path !== '/' && currentPath.startsWith(item.path));
        return (
          <ListItemButton
            key={item.path}
            selected={active}
            onClick={() => onNavigate(item.path)}
            sx={{
              borderRadius: 1,
              mb: 0.5,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
                '&:hover': { bgcolor: 'primary.dark' },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ variant: 'body2' }} />
          </ListItemButton>
        );
      })}
    </List>

    <Divider />

    <List dense sx={{ px: 1, py: 1 }}>
      {bottomItems.map((item) => (
        <ListItemButton
          key={item.path}
          onClick={() => onNavigate(item.path)}
          sx={{ borderRadius: 1 }}
        >
          <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
          <ListItemText primary={item.label} primaryTypographyProps={{ variant: 'body2' }} />
        </ListItemButton>
      ))}
    </List>

    <Box sx={{ px: 2, pb: 2 }}>
      <Chip label="v1.0.0" size="small" variant="outlined" sx={{ fontSize: 10 }} />
    </Box>
  </Box>
);

const Sidebar: React.FC<SidebarProps> = ({ drawerWidth, mobileOpen, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigate = (path: string) => {
    navigate(path);
    onClose();
  };

  const drawer = <DrawerContent onNavigate={handleNavigate} currentPath={location.pathname} />;

  return (
    <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
      {/* Mobile */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{ display: { xs: 'block', sm: 'none' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
      >
        {drawer}
      </Drawer>
      {/* Desktop */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            borderRight: '1px solid',
            borderColor: 'divider',
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;
