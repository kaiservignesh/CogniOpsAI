import {
  Box,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
} from "@mui/material";
import { Link } from "react-router-dom";

const menuItems = [
  { label: "Dashboard", path: "/" },
  { label: "Alerts", path: "/alerts" },
  { label: "Situations", path: "/situations" },
  { label: "Workflows", path: "/workflows" },
  {
    label: "Executions",
    path: "/workflow-executions",
  },
];

export default function Sidebar() {
  return (
    <Box
      sx={{
        width: 230,
        borderRight: 1,
        borderColor: "divider",
      }}
    >
      <Toolbar />

      <Divider />

      <List>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            component={Link}
            to={item.path}
          >
            <ListItemText
              primary={item.label}
            />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
}