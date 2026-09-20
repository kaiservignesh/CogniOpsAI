import { useQuery } from "@tanstack/react-query";
import {
  Alert as MuiAlert,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Typography,
} from "@mui/material";

import { getAlerts } from "../api/alerts";
import { getSituations } from "../api/situations";
import { getWorkflowExecutions } from "../api/workflows";

export default function Dashboard() {
  const alertsQuery = useQuery({
    queryKey: ["alerts"],
    queryFn: getAlerts,
  });

  const situationsQuery = useQuery({
    queryKey: ["situations"],
    queryFn: getSituations,
  });

  const executionsQuery = useQuery({
    queryKey: ["workflow-executions"],
    queryFn: getWorkflowExecutions,
  });

  if (
    alertsQuery.isLoading ||
    situationsQuery.isLoading ||
    executionsQuery.isLoading
  ) {
    return <LinearProgress />;
  }

  if (
    alertsQuery.isError ||
    situationsQuery.isError ||
    executionsQuery.isError
  ) {
    return (
      <MuiAlert severity="error">
        Unable to load dashboard data. Please verify that
        the backend is running and that your JWT session is
        valid.
      </MuiAlert>
    );
  }

  const alerts = alertsQuery.data ?? [];
  const situations = situationsQuery.data ?? [];
  const executions = executionsQuery.data ?? [];

  const totalAlerts = alerts.length;

  const openSituations = situations.filter(
    (situation) =>
      situation.status === "Open" ||
      situation.status === "Investigating",
  ).length;

  const criticalSituations = situations.filter(
    (situation) =>
      situation.severity.toLowerCase() === "critical",
  ).length;

  const aiAnalyzedSituations = situations.filter(
    (situation) => situation.ai_status === "Completed",
  ).length;

  const successfulExecutions = executions.filter(
    (execution) => execution.status === "Success",
  ).length;

  const cards = [
    { title: "Total Alerts", value: totalAlerts },
    { title: "Open Situations", value: openSituations },
    {
      title: "Critical Situations",
      value: criticalSituations,
    },
    { title: "AI Analyzed", value: aiAnalyzedSituations },
    {
      title: "Workflow Success",
      value: successfulExecutions,
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        CogniOpsAI operational overview
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, minmax(0, 1fr))",
            md: "repeat(3, minmax(0, 1fr))",
            lg: "repeat(5, minmax(0, 1fr))",
          },
          gap: 2.5,
          alignItems: "stretch",
        }}
      >
        {cards.map((card) => (
          <Card
            key={card.title}
            sx={{
              height: "100%",
              minHeight: 132,
            }}
          >
            <CardContent
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                p: 2.5,
                "&:last-child": {
                  pb: 2.5,
                },
              }}
            >
              <Typography
                color="text.secondary"
                variant="body2"
                sx={{
                  fontWeight: 600,
                  lineHeight: 1.3,
                }}
              >
                {card.title}
              </Typography>

              <Typography
                variant="h3"
                sx={{
                  fontWeight: 800,
                  lineHeight: 1,
                  mt: 2,
                }}
              >
                {card.value}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Card sx={{ mt: 3 }}>
        <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
          <Typography variant="h6" gutterBottom>
            Recent Workflow Executions
          </Typography>

          {executions.length === 0 ? (
            <Typography color="text.secondary">
              No workflow executions found.
            </Typography>
          ) : (
            <Box>
              {executions.slice(0, 5).map((execution) => (
                <Box
                  key={execution.id}
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    py: 1,
                    borderBottom: 1,
                    borderColor: "divider",
                    "&:last-child": {
                      borderBottom: 0,
                    },
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{ flex: 1 }}
                  >
                    Execution #{execution.id} —{" "}
                    {execution.action_type ?? "Unknown"}
                  </Typography>

                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 700,
                      color:
                        execution.status === "Success"
                          ? "success.main"
                          : "text.primary",
                    }}
                  >
                    {execution.status}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
