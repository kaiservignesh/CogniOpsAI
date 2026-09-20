import {
  Box,
  Button,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
} from "@mui/material";
import { Link, useLocation } from "react-router-dom";

import { logout } from "../../api/client";

const menuItems = [
  { label: "Dashboard", path: "/" },
  { label: "Alerts", path: "/alerts" },
  { label: "Situations", path: "/situations" },
  {
    label: "Notification Workflows",
    path: "/workflows",
  },
  {
    label: "Notification Workflow Builder",
    path: "/workflow-builder",
  },
  {
    label: "Correlation Workflows",
    path: "/correlation-workflows",
  },
  {
    label: "Correlation Workflow Builder",
    path: "/correlation-workflow-builder",
  },
  {
    label: "Workflow Executions",
    path: "/workflow-executions",
  },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <Box
      component="aside"
      sx={{
        width: { xs: 210, sm: 250 },
        flexShrink: 0,
        minHeight: "100vh",
        borderRight: 1,
        borderColor: "divider",
        bgcolor: "background.paper",
        position: "sticky",
        top: 0,
        alignSelf: "flex-start",
      }}
    >
      <Toolbar />
      <Divider />

      <List sx={{ px: 1.25, py: 1.5 }}>
        {menuItems.map((item) => {
          const selected =
            item.path === "/"
              ? location.pathname === "/"
              : location.pathname === item.path ||
                location.pathname.startsWith(
                  `${item.path}/`,
                );

          return (
            <ListItemButton
              key={item.path}
              component={Link}
              to={item.path}
              selected={selected}
              sx={{
                borderRadius: 1.5,
                mb: 0.5,
                minHeight: 40,
                px: 1.5,
                "&.Mui-selected": {
                  bgcolor: "action.selected",
                  color: "primary.main",
                  "& .MuiTypography-root": {
                    fontWeight: 700,
                  },
                },
                "&.Mui-selected:hover": {
                  bgcolor: "action.hover",
                },
              }}
            >
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: 14,
                  lineHeight: 1.35,
                }}
              />
            </ListItemButton>
          );
        })}
      </List>

      <Box sx={{ p: 2, mt: "auto" }}>
        <Button
          fullWidth
          variant="outlined"
          color="error"
          onClick={logout}
        >
          Logout
        </Button>
      </Box>
    </Box>
  );
}
