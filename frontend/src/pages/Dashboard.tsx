import { useQuery } from "@tanstack/react-query";
import {
  Alert as MuiAlert,
  Card,
  CardContent,
  Grid,
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
        Unable to load dashboard data.
        Please verify that the backend is running and
        that your JWT session is valid.
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
      situation.severity.toLowerCase() ===
      "critical",
  ).length;

  const aiAnalyzedSituations = situations.filter(
    (situation) =>
      situation.ai_status === "Completed",
  ).length;

  const successfulExecutions = executions.filter(
    (execution) =>
      execution.status === "Success",
  ).length;

  const cards = [
    {
      title: "Total Alerts",
      value: totalAlerts,
    },
    {
      title: "Open Situations",
      value: openSituations,
    },
    {
      title: "Critical Situations",
      value: criticalSituations,
    },
    {
      title: "AI Analyzed",
      value: aiAnalyzedSituations,
    },
    {
      title: "Workflow Success",
      value: successfulExecutions,
    },
  ];

  return (
    <>
      <Typography
        variant="h4"
        fontWeight={700}
        gutterBottom
      >
        Dashboard
      </Typography>

      <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
      >
        CogniOpsAI operational overview
      </Typography>

      <Grid container spacing={3}>
        {cards.map((card) => (
          <Grid
            key={card.title}
            size={{
              xs: 12,
              sm: 6,
              md: 4,
              lg: 2.4,
            }}
          >
            <Card>
              <CardContent>
                <Typography
                  color="text.secondary"
                  variant="body2"
                  gutterBottom
                >
                  {card.title}
                </Typography>

                <Typography
                  variant="h3"
                  fontWeight={700}
                >
                  {card.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography
            variant="h6"
            fontWeight={600}
            gutterBottom
          >
            Recent Workflow Executions
          </Typography>

          {executions.length === 0 ? (
            <Typography color="text.secondary">
              No workflow executions found.
            </Typography>
          ) : (
            executions.slice(0, 5).map(
              (execution) => (
                <Typography
                  key={execution.id}
                  variant="body2"
                  sx={{ py: 0.75 }}
                >
                  Execution #{execution.id} —{" "}
                  {execution.action_type ?? "Unknown"} —{" "}
                  {execution.status}
                </Typography>
              ),
            )
          )}
        </CardContent>
      </Card>
    </>
  );
}