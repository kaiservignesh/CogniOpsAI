import {
  Box,
  Button,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
} from "@mui/material";
import { Link } from "react-router-dom";

import { logout } from "../../api/client";

const menuItems = [
  {
    label: "Dashboard",
    path: "/",
  },
  {
    label: "Alerts",
    path: "/alerts",
  },
  {
    label: "Situations",
    path: "/situations",
  },

  // Notification workflow section
  {
    label: "Notification Workflows",
    path: "/workflows",
  },
  {
    label: "Notification Workflow Builder",
    path: "/workflow-builder",
  },

  // Correlation workflow section
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
  return (
    <Box
      sx={{
        width: 250,
        flexShrink: 0,
        borderRight: 1,
        borderColor: "divider",
        backgroundColor: "background.paper",
      }}
    >
      <Toolbar />

      <Divider />

      <List sx={{ px: 1 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            component={Link}
            to={item.path}
            sx={{
              borderRadius: 1,
              mb: 0.5,
            }}
          >
            <ListItemText
              primary={item.label}
              primaryTypographyProps={{
                fontSize: 14,
              }}
            />
          </ListItemButton>
        ))}
      </List>

      <Box sx={{ p: 2 }}>
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