import apiClient from "./client";

export interface WorkflowPolicy {
  id: number;
  name: string;
  description?: string | null;
  enabled: boolean;
  condition: Record<string, unknown>;
  action: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface WorkflowPolicyInput {
  name: string;
  description?: string;
  enabled: boolean;
  condition: Record<string, unknown>;
  action: Record<string, unknown>;
}

export interface WorkflowExecution {
  id: number;
  situation_id: number;
  policy_id: number;
  status: string;
  action_type?: string | null;
  action_target?: string | null;
  action_payload?: Record<string, unknown> | null;
  result?: string | null;
  created_at: string;
  updated_at: string;
}

export async function getWorkflowPolicies(): Promise<
  WorkflowPolicy[]
> {
  const response = await apiClient.get<WorkflowPolicy[]>(
    "/workflows/policies/",
  );

  return response.data;
}

export async function createWorkflowPolicy(
  policy: WorkflowPolicyInput,
): Promise<WorkflowPolicy> {
  const response =
    await apiClient.post<WorkflowPolicy>(
      "/workflows/policies/",
      policy,
    );

  return response.data;
}

export async function updateWorkflowPolicy(
  policyId: number,
  policy: Partial<WorkflowPolicyInput>,
): Promise<WorkflowPolicy> {
  const response =
    await apiClient.put<WorkflowPolicy>(
      `/workflows/policies/${policyId}`,
      policy,
    );

  return response.data;
}

export async function getWorkflowExecutions(): Promise<
  WorkflowExecution[]
> {
  const response =
    await apiClient.get<WorkflowExecution[]>(
      "/workflows/policies/executions/",
    );

  return response.data;
}