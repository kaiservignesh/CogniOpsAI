import { useCallback, useMemo, useState } from "react";
import {
  addEdge,
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import {
  Alert as MuiAlert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { createWorkflowPolicy, type WorkflowPolicyInput } from "../api/workflows";

type BuilderData = {
  label: string;
  subtitle: string;
  tone: "primary" | "warning" | "info" | "success";
};

type BuilderNode = Node<BuilderData>;

const initialNodes: BuilderNode[] = [
  {
    id: "policy",
    position: { x: 40, y: 160 },
    data: {
      label: "Policy",
      subtitle: "Workflow identity",
      tone: "primary",
    },
    type: "builder",
  },
  {
    id: "condition",
    position: { x: 330, y: 160 },
    data: {
      label: "Condition",
      subtitle: "When should it run?",
      tone: "warning",
    },
    type: "builder",
  },
  {
    id: "tag",
    position: { x: 630, y: 160 },
    data: {
      label: "Tag",
      subtitle: "Match an alert tag",
      tone: "info",
    },
    type: "builder",
  },
  {
    id: "notification",
    position: { x: 930, y: 160 },
    data: {
      label: "Notification",
      subtitle: "Execute response",
      tone: "success",
    },
    type: "builder",
  },
];

const initialEdges: Edge[] = [
  {
    id: "policy-condition",
    source: "policy",
    target: "condition",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "condition-tag",
    source: "condition",
    target: "tag",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "tag-notification",
    source: "tag",
    target: "notification",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
];

function BuilderNode({ data }: { data: BuilderData }) {
  const toneMap = {
    primary: "primary.main",
    warning: "warning.main",
    info: "info.main",
    success: "success.main",
  } as const;

  return (
    <Box
      sx={{
        minWidth: 190,
        border: 2,
        borderColor: toneMap[data.tone],
        borderRadius: 2,
        bgcolor: "background.paper",
        boxShadow: 2,
        px: 2,
        py: 1.5,
      }}
    >
      <Handle type="target" position={Position.Left} />
      <Typography fontWeight={800}>{data.label}</Typography>
      <Typography variant="caption" color="text.secondary">
        {data.subtitle}
      </Typography>
      <Handle type="source" position={Position.Right} />
    </Box>
  );
}

const nodeTypes = { builder: BuilderNode };

export default function WorkflowBuilder() {
  const [nodes, setNodes, onNodesChange] = useNodesState<BuilderNode>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const [policyName, setPolicyName] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("Critical");
  const [environment, setEnvironment] = useState("production");
  const [service, setService] = useState("");
  const [source, setSource] = useState("");
  const [policyNameMatch, setPolicyNameMatch] = useState("");
  const [tagKey, setTagKey] = useState("");
  const [tagValue, setTagValue] = useState("");
  const [actionType, setActionType] = useState("email");
  const [recipient, setRecipient] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const conditionPreview = useMemo(() => {
    const condition: Record<string, unknown> = { severity };
    if (environment.trim()) condition.environment = environment.trim();
    if (service.trim()) condition.service = service.trim();
    if (source.trim()) condition.source = source.trim();
    if (policyNameMatch.trim()) condition.policy_name = policyNameMatch.trim();
    if (tagKey.trim() && tagValue.trim()) {
      condition.tag = `${tagKey.trim()}:${tagValue.trim()}`;
    }
    return condition;
  }, [environment, policyNameMatch, service, severity, source, tagKey, tagValue]);

  const actionPreview = useMemo(() => {
    const action: Record<string, unknown> = {
      type: actionType,
      target: actionType === "email" ? "operations" : actionType,
    };
    if (actionType === "email") {
      action.recipient = recipient.trim();
      action.subject = policyName.trim() || "CogniOpsAI workflow notification";
      action.body = description.trim() || "CogniOpsAI workflow notification.";
    }
    return action;
  }, [actionType, description, policyName, recipient]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((currentEdges) =>
        addEdge(
          {
            ...connection,
            markerEnd: { type: MarkerType.ArrowClosed },
          },
          currentEdges,
        ),
      );
    },
    [setEdges],
  );

  const handleSave = async () => {
    setMessage("");

    if (!policyName.trim()) {
      setMessage("Policy name is required.");
      return;
    }

    if (actionType === "email" && !recipient.trim()) {
      setMessage("Recipient is required for email actions.");
      return;
    }

    if (tagKey.trim() !== "" && tagValue.trim() === "") {
      setMessage("Enter a tag value or clear the tag key.");
      return;
    }

    const policy: WorkflowPolicyInput = {
      name: policyName.trim(),
      description: description.trim() || undefined,
      enabled: true,
      condition: conditionPreview,
      action: actionPreview,
    };

    try {
      setSaving(true);
      await createWorkflowPolicy(policy);
      setMessage("Visual workflow saved successfully.");
      setPolicyName("");
      setDescription("");
      setService("");
      setSource("");
      setPolicyNameMatch("");
      setTagKey("");
      setTagValue("");
      setRecipient("");
    } catch {
      setMessage("Unable to create workflow policy. Check the API and policy name.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", md: "center" }}
        spacing={2}
        sx={{ mb: 3 }}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Visual Workflow Builder
          </Typography>
          <Typography color="text.secondary">
            Build a condition-driven incident response flow using connected nodes.
          </Typography>
        </Box>
        <Button component={RouterLink} to="/workflows" variant="outlined">
          Back to Policies
        </Button>
      </Stack>

      <Stack spacing={3}>
        <Card>
          <CardContent>
            <Stack spacing={2}>
              <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                <TextField
                  fullWidth
                  label="Policy Name"
                  value={policyName}
                  onChange={(event) => setPolicyName(event.target.value)}
                />
                <TextField
                  fullWidth
                  label="Description"
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                />
              </Stack>
              <Chip
                label="Policy → Condition → Tag → Notification"
                variant="outlined"
                sx={{ width: "fit-content" }}
              />
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={800} gutterBottom>
              Workflow Canvas
            </Typography>
            <Box
              sx={{
                height: 430,
                border: 1,
                borderColor: "divider",
                borderRadius: 2,
                overflow: "hidden",
              }}
            >
              <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
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

        <Stack direction={{ xs: "column", lg: "row" }} spacing={3}>
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={800} gutterBottom>
                Condition Node
              </Typography>
              <Stack spacing={2}>
                <FormControl fullWidth>
                  <InputLabel>Severity</InputLabel>
                  <Select
                    value={severity}
                    label="Severity"
                    onChange={(event) => setSeverity(event.target.value)}
                  >
                    <MenuItem value="Critical">Critical</MenuItem>
                    <MenuItem value="High">High</MenuItem>
                    <MenuItem value="Medium">Medium</MenuItem>
                    <MenuItem value="Low">Low</MenuItem>
                  </Select>
                </FormControl>
                <TextField
                  fullWidth
                  label="Environment"
                  value={environment}
                  onChange={(event) => setEnvironment(event.target.value)}
                />
                <TextField
                  fullWidth
                  label="Service (optional)"
                  value={service}
                  onChange={(event) => setService(event.target.value)}
                />
                <TextField
                  fullWidth
                  label="Source (optional)"
                  placeholder="Grafana / New Relic / Loki"
                  value={source}
                  onChange={(event) => setSource(event.target.value)}
                />
                <TextField
                  fullWidth
                  label="Policy Name Match (optional)"
                  value={policyNameMatch}
                  onChange={(event) => setPolicyNameMatch(event.target.value)}
                />
              </Stack>
            </CardContent>
          </Card>

          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={800} gutterBottom>
                Tag Node
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Match a tag from an alert in the Situation.
              </Typography>
              <Stack spacing={2}>
                <TextField
                  fullWidth
                  label="Tag Key"
                  placeholder="environment"
                  value={tagKey}
                  onChange={(event) => setTagKey(event.target.value)}
                />
                <TextField
                  fullWidth
                  label="Tag Value"
                  placeholder="production"
                  value={tagValue}
                  onChange={(event) => setTagValue(event.target.value)}
                />
                <MuiAlert severity="info">
                  Saved as <strong>{tagKey || "tag"}:{tagValue || "value"}</strong> in the policy condition.
                </MuiAlert>
              </Stack>
            </CardContent>
          </Card>

          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={800} gutterBottom>
                Notification Node
              </Typography>
              <Stack spacing={2}>
                <FormControl fullWidth>
                  <InputLabel>Action Type</InputLabel>
                  <Select
                    value={actionType}
                    label="Action Type"
                    onChange={(event) => setActionType(event.target.value)}
                  >
                    <MenuItem value="email">Email</MenuItem>
                    <MenuItem value="notification">Mock Notification</MenuItem>
                    <MenuItem value="servicenow">ServiceNow</MenuItem>
                    <MenuItem value="xmatters">xMatters</MenuItem>
                  </Select>
                </FormControl>
                {actionType === "email" && (
                  <TextField
                    fullWidth
                    label="Recipient Email"
                    value={recipient}
                    onChange={(event) => setRecipient(event.target.value)}
                  />
                )}
              </Stack>
            </CardContent>
          </Card>
        </Stack>

        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={800} gutterBottom>
              Generated Policy
            </Typography>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Condition JSON
                </Typography>
                <Box
                  component="pre"
                  sx={{
                    m: 0,
                    p: 2,
                    bgcolor: "action.hover",
                    borderRadius: 2,
                    overflow: "auto",
                    fontSize: 13,
                  }}
                >
                  {JSON.stringify(conditionPreview, null, 2)}
                </Box>
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Action JSON
                </Typography>
                <Box
                  component="pre"
                  sx={{
                    m: 0,
                    p: 2,
                    bgcolor: "action.hover",
                    borderRadius: 2,
                    overflow: "auto",
                    fontSize: 13,
                  }}
                >
                  {JSON.stringify(actionPreview, null, 2)}
                </Box>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        <Stack direction="row" justifyContent="flex-end">
          <Button
            variant="contained"
            size="large"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Workflow"}
          </Button>
        </Stack>

        <Snackbar
          open={Boolean(message)}
          autoHideDuration={4500}
          onClose={() => setMessage("")}
        >
          <MuiAlert severity={message.includes("success") ? "success" : "error"}>
            {message}
          </MuiAlert>
        </Snackbar>
      </Stack>
    </Box>
  );
}
