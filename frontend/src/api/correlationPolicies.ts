import apiClient from "./client";

export interface CorrelationRule {
  field: string;
  operator: string;
  value: string;
}

export interface CorrelationCondition {
  match: "all" | "any";
  rules: CorrelationRule[];
}

export interface CorrelationPolicy {
  id: number;
  name: string;
  description?: string | null;
  enabled: boolean;
  condition: CorrelationCondition;
  time_window_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface CorrelationPolicyInput {
  name: string;
  description?: string;
  enabled: boolean;
  condition: CorrelationCondition;
  time_window_minutes: number;
}

export async function getCorrelationPolicies(): Promise<
  CorrelationPolicy[]
> {
  const response = await apiClient.get<CorrelationPolicy[]>(
    "/correlation/policies/",
  );

  return response.data;
}

export async function getCorrelationPolicy(
  policyId: number,
): Promise<CorrelationPolicy> {
  const response = await apiClient.get<CorrelationPolicy>(
    `/correlation/policies/${policyId}`,
  );

  return response.data;
}

export async function createCorrelationPolicy(
  policy: CorrelationPolicyInput,
): Promise<CorrelationPolicy> {
  const response = await apiClient.post<CorrelationPolicy>(
    "/correlation/policies/",
    policy,
  );

  return response.data;
}

export async function updateCorrelationPolicy(
  policyId: number,
  policy: Partial<CorrelationPolicyInput>,
): Promise<CorrelationPolicy> {
  const response = await apiClient.put<CorrelationPolicy>(
    `/correlation/policies/${policyId}`,
    policy,
  );

  return response.data;
}