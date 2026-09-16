import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  addEdge,
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  type Connection,
  type Edge,
  type Node,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import {
  createWorkflowPolicy,
  getWorkflowPolicies,
  updateWorkflowPolicy,
  type WorkflowPolicyInput,
} from "../api/workflows";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

const initialNodes: Node[] = [
  {
    id: "condition",
    position: {
      x: 100,
      y: 150,
    },
    data: {
      label: "Condition",
    },
    type: "condition",
  },
  {
    id: "action",
    position: {
      x: 500,
      y: 150,
    },
    data: {
      label: "Action",
    },
    type: "action",
  },
];

const initialEdges: Edge[] = [
  {
    id: "condition-action",
    source: "condition",
    target: "action",
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
];

function ConditionNode({
  data,
}: {
  data: {
    label: string;
  };
}) {
  return (
    <Box
      sx={{
        minWidth: 180,
        border: 2,
        borderColor: "primary.main",
        borderRadius: 2,
        bgcolor: "background.paper",
        p: 2,
      }}
    >
      <Handle
        type="source"
        position={Position.Right}
      />

      <Typography fontWeight={700}>
        {data.label}
      </Typography>

      <Typography
        variant="body2"
        color="text.secondary"
      >
        Alert / Situation condition
      </Typography>
    </Box>
  );
}

function ActionNode({
  data,
}: {
  data: {
    label: string;
  };
}) {
  return (
    <Box
      sx={{
        minWidth: 180,
        border: 2,
        borderColor: "success.main",
        borderRadius: 2,
        bgcolor: "background.paper",
        p: 2,
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
      />

      <Typography fontWeight={700}>
        {data.label}
      </Typography>

      <Typography
        variant="body2"
        color="text.secondary"
      >
        Execute workflow action
      </Typography>
    </Box>
  );
}

const nodeTypes = {
  condition: ConditionNode,
  action: ActionNode,
};

export default function WorkflowBuilder() {
  const navigate = useNavigate();

  const { id } =
    useParams<{
      id?: string;
    }>();

  const editingId = id
    ? Number(id)
    : null;

  const [
    nodes,
    ,
    onNodesChange,
  ] = useNodesState(
    initialNodes,
  );

  const [
    edges,
    setEdges,
    onEdgesChange,
  ] = useEdgesState(
    initialEdges,
  );

  const [
    policyName,
    setPolicyName,
  ] = useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    severity,
    setSeverity,
  ] = useState("Critical");

  const [
    environment,
    setEnvironment,
  ] = useState("production");

  const [
    service,
    setService,
  ] = useState("");

  const [
    actionType,
    setActionType,
  ] = useState("email");

  const [
    recipient,
    setRecipient,
  ] = useState("");

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    message,
    setMessage,
  ] = useState("");

  const [
    loadingPolicy,
    setLoadingPolicy,
  ] = useState(
    Boolean(editingId),
  );

  /*
   * Load existing notification workflow
   * when editing.
   */
  useEffect(() => {
    if (!editingId) {
      setLoadingPolicy(false);
      return;
    }

    getWorkflowPolicies()
      .then((policies) => {
        const policy = policies.find(
          (item) =>
            item.id === editingId,
        );

        if (!policy) {
          setMessage(
            "Notification workflow not found.",
          );
          return;
        }

        const condition =
          policy.condition ?? {};

        const action =
          policy.action ?? {};

        setPolicyName(
          policy.name,
        );

        setDescription(
          policy.description ?? "",
        );

        setSeverity(
          String(
            condition.severity ??
              "Critical",
          ),
        );

        setEnvironment(
          String(
            condition.environment ??
              "production",
          ),
        );

        setService(
          String(
            condition.service ??
              "",
          ),
        );

        setActionType(
          String(
            action.type ??
              "email",
          ),
        );

        setRecipient(
          String(
            action.recipient ??
              "",
          ),
        );
      })
      .catch(() => {
        setMessage(
          "Unable to load notification workflow.",
        );
      })
      .finally(() => {
        setLoadingPolicy(false);
      });
  }, [editingId]);

  /*
   * React Flow connection handling.
   */
  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges(
        (currentEdges) =>
          addEdge(
            {
              ...connection,
              markerEnd: {
                type: MarkerType.ArrowClosed,
              },
            },
            currentEdges,
          ),
      );
    },
    [setEdges],
  );

  /*
   * Build the same JSON payload used
   * when creating/updating the policy.
   */
  const workflowJson = useMemo(
    () => {
      const condition: Record<
        string,
        unknown
      > = {
        severity,
        environment,
      };

      if (service.trim()) {
        condition.service =
          service.trim();
      }

      const action: Record<
        string,
        unknown
      > = {
        type: actionType,
        target:
          actionType === "email"
            ? "operations"
            : actionType,
      };

      if (
        actionType === "email"
      ) {
        action.recipient =
          recipient.trim();

        action.subject =
          policyName;

        action.body =
          description.trim() ||
          "CogniOpsAI workflow notification.";
      }

      const policy:
        WorkflowPolicyInput = {
          name:
            policyName.trim(),
          description:
            description.trim() ||
            undefined,
          enabled: true,
          condition,
          action,
        };

      return policy;
    },
    [
      policyName,
      description,
      severity,
      environment,
      service,
      actionType,
      recipient,
    ],
  );

  const jsonPreview = useMemo(
    () =>
      JSON.stringify(
        workflowJson,
        null,
        2,
      ),
    [workflowJson],
  );

  /*
   * Save / update notification workflow.
   */
  const handleSave = async () => {
    setMessage("");

    if (!policyName.trim()) {
      setMessage(
        "Policy name is required.",
      );
      return;
    }

    if (
      actionType === "email" &&
      !recipient.trim()
    ) {
      setMessage(
        "Recipient is required for email actions.",
      );
      return;
    }

    try {
      setSaving(true);

      if (editingId) {
        await updateWorkflowPolicy(
          editingId,
          workflowJson,
        );

        setMessage(
          "Notification workflow updated successfully.",
        );

        setTimeout(() => {
          navigate(
            "/workflows",
          );
        }, 600);
      } else {
        await createWorkflowPolicy(
          workflowJson,
        );

        setMessage(
          "Notification workflow created successfully.",
        );

        setPolicyName("");
        setDescription("");
        setService("");
        setRecipient("");
      }
    } catch {
      setMessage(
        editingId
          ? "Unable to update workflow policy."
          : "Unable to create workflow policy.",
      );
    } finally {
      setSaving(false);
    }
  };

  if (loadingPolicy) {
    return (
      <Typography>
        Loading notification workflow...
      </Typography>
    );
  }

  return (
    <Box>
      {/* =====================================================
          Page Header
         ===================================================== */}

      <Typography
        variant="h4"
        fontWeight={700}
        gutterBottom
      >
        {editingId
          ? "Edit Notification Workflow"
          : "Notification Workflow Builder"}
      </Typography>

      <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
      >
        Define a condition-driven automation
        workflow for incident notifications.
      </Typography>

      <Stack spacing={3}>
        {/* ===================================================
            Policy Configuration
           =================================================== */}

        <Card>
          <CardContent>
            <Typography
              variant="h6"
              fontWeight={700}
              gutterBottom
            >
              Policy Configuration
            </Typography>

            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Policy Name"
                value={policyName}
                onChange={(event) =>
                  setPolicyName(
                    event.target.value,
                  )
                }
              />

              <TextField
                fullWidth
                label="Description"
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
              />

              <Stack
                direction={{
                  xs: "column",
                  md: "row",
                }}
                spacing={2}
              >
                <FormControl fullWidth>
                  <InputLabel>
                    Severity
                  </InputLabel>

                  <Select
                    value={severity}
                    label="Severity"
                    onChange={(event) =>
                      setSeverity(
                        event.target.value,
                      )
                    }
                  >
                    <MenuItem value="Critical">
                      Critical
                    </MenuItem>

                    <MenuItem value="High">
                      High
                    </MenuItem>

                    <MenuItem value="Medium">
                      Medium
                    </MenuItem>

                    <MenuItem value="Low">
                      Low
                    </MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  label="Environment"
                  value={environment}
                  onChange={(event) =>
                    setEnvironment(
                      event.target.value,
                    )
                  }
                />

                <TextField
                  fullWidth
                  label="Service"
                  value={service}
                  onChange={(event) =>
                    setService(
                      event.target.value,
                    )
                  }
                />
              </Stack>

              <FormControl fullWidth>
                <InputLabel>
                  Action Type
                </InputLabel>

                <Select
                  value={actionType}
                  label="Action Type"
                  onChange={(event) =>
                    setActionType(
                      event.target.value,
                    )
                  }
                >
                  <MenuItem value="email">
                    Email
                  </MenuItem>

                  <MenuItem value="notification">
                    Mock Notification
                  </MenuItem>

                  <MenuItem value="servicenow">
                    ServiceNow
                  </MenuItem>

                  <MenuItem value="xmatters">
                    xMatters
                  </MenuItem>
                </Select>
              </FormControl>

              {actionType ===
                "email" && (
                <TextField
                  fullWidth
                  label="Recipient Email"
                  value={recipient}
                  onChange={(event) =>
                    setRecipient(
                      event.target.value,
                    )
                  }
                />
              )}
            </Stack>
          </CardContent>
        </Card>

        {/* ===================================================
            React Flow
           =================================================== */}

        <Card>
          <CardContent>
            <Typography
              variant="h6"
              fontWeight={700}
              gutterBottom
            >
              Notification Workflow
            </Typography>

            <Box
              sx={{
                height: 420,
                border: 1,
                borderColor:
                  "divider",
                borderRadius: 2,
              }}
            >
              <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                onNodesChange={
                  onNodesChange
                }
                onEdgesChange={
                  onEdgesChange
                }
                onConnect={onConnect}
                fitView
              >
                <Background />
                <Controls />
                <MiniMap />
              </ReactFlow>
            </Box>
          </CardContent>
        </Card>

        {/* ===================================================
            JSON Preview
           =================================================== */}

        <Card>
          <CardContent>
            <Stack
              direction={{
                xs: "column",
                sm: "row",
              }}
              justifyContent="space-between"
              alignItems={{
                xs: "flex-start",
                sm: "center",
              }}
              spacing={2}
              sx={{ mb: 2 }}
            >
              <Box>
                <Typography
                  variant="h6"
                  fontWeight={700}
                >
                  JSON Preview
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                >
                  This JSON is generated automatically
                  from the notification workflow
                  configuration above.
                </Typography>
              </Box>

              <Button
                variant="outlined"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(
                      jsonPreview,
                    );

                    setMessage(
                      "JSON copied to clipboard.",
                    );
                  } catch {
                    setMessage(
                      "Unable to copy JSON to clipboard.",
                    );
                  }
                }}
              >
                Copy JSON
              </Button>
            </Stack>

            <TextField
              fullWidth
              multiline
              minRows={14}
              value={jsonPreview}
              InputProps={{
                readOnly: true,
              }}
              inputProps={{
                style: {
                  fontFamily:
                    "monospace",
                  fontSize:
                    "13px",
                },
              }}
            />
          </CardContent>
        </Card>

        {/* ===================================================
            Save / Update
           =================================================== */}

        <Stack
          direction="row"
          justifyContent="flex-end"
        >
          <Button
            variant="contained"
            size="large"
            onClick={handleSave}
            disabled={saving}
          >
            {saving
              ? "Saving..."
              : editingId
                ? "Update Notification Workflow"
                : "Save Notification Workflow"}
          </Button>
        </Stack>

        {/* ===================================================
            Messages
           =================================================== */}

        <Snackbar
          open={Boolean(message)}
          autoHideDuration={4000}
          onClose={() =>
            setMessage("")
          }
          message={message}
        />
      </Stack>
    </Box>
  );
}
