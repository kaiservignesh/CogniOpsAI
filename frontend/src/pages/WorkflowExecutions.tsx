import { useQuery } from "@tanstack/react-query";
import {
  Alert as MuiAlert,
  Box,
  Chip,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import { getWorkflowExecutions } from "../api/workflows";

export default function WorkflowExecutions() {
  const {
    data: executions = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["workflow-executions"],
    queryFn: getWorkflowExecutions,
  });

  if (isLoading) {
    return <LinearProgress />;
  }

  if (isError) {
    return (
      <MuiAlert severity="error">
        Unable to load workflow executions.
      </MuiAlert>
    );
  }

  return (
    <Box>
      <Typography
        variant="h4"
        fontWeight={700}
        gutterBottom
      >
        Workflow Executions
      </Typography>

      <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
      >
        Monitor automated workflow actions and their results.
      </Typography>

      <TableContainer
        component={Paper}
        elevation={2}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Situation</TableCell>
              <TableCell>Policy</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Target</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Result</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {executions.map((execution) => (
              <TableRow
                key={execution.id}
                hover
              >
                <TableCell>
                  #{execution.id}
                </TableCell>

                <TableCell>
                  #{execution.situation_id}
                </TableCell>

                <TableCell>
                  #{execution.policy_id}
                </TableCell>

                <TableCell>
                  {execution.action_type ?? "—"}
                </TableCell>

                <TableCell>
                  {execution.action_target ?? "—"}
                </TableCell>

                <TableCell>
                  <Chip
                    label={execution.status}
                    size="small"
                    color={
                      execution.status === "Success"
                        ? "success"
                        : execution.status === "Failed"
                          ? "error"
                          : "default"
                    }
                  />
                </TableCell>

                <TableCell>
                  <Typography
                    variant="body2"
                    sx={{
                      maxWidth: 400,
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {execution.result ?? "—"}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}

            {executions.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={7}
                  align="center"
                >
                  No workflow executions found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}