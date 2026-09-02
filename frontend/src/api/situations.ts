import apiClient from "./client";

export interface SituationAlert {
  id: number;
  title: string;
  source: string;
  severity: string;
  service?: string | null;
  environment?: string | null;
  policy_name?: string | null;
  tags?: string | null;
}

export interface Situation {
  id: number;
  title: string;
  description?: string | null;
  severity: string;
  status: string;
  service?: string | null;
  environment?: string | null;
  created_at: string;
  updated_at: string;
  alert_count: number;

  correlation_score?: number | null;
  correlation_method?: string | null;
  correlation_reasons?: string[] | null;

  ai_summary?: string | null;
  ai_root_cause?: string | null;
  ai_recommendations?: string | null;
  ai_status: string;
  ai_updated_at?: string | null;
}

export interface SituationContext
  extends Situation {
  alerts: SituationAlert[];
}

export async function getSituations(): Promise<Situation[]> {
  const response = await apiClient.get<Situation[]>(
    "/situations/",
  );

  return response.data;
}

export async function getSituation(
  situationId: number,
): Promise<Situation> {
  const response = await apiClient.get<Situation>(
    `/situations/${situationId}`,
  );

  return response.data;
}

export async function getSituationContext(
  situationId: number,
): Promise<SituationContext> {
  const response =
    await apiClient.get<SituationContext>(
      `/situations/${situationId}/context`,
    );

  return response.data;
}

export async function updateSituationStatus(
  situationId: number,
  status: string,
): Promise<Situation> {
  const response = await apiClient.patch<Situation>(
    `/situations/${situationId}/status`,
    { status },
  );

  return response.data;
}

export async function analyzeSituation(
  situationId: number,
): Promise<{
  situation_id: number;
  ai_status: string;
  ai_summary: string | null;
  ai_root_cause: string | null;
  ai_recommendations: string | null;
  ai_updated_at: string | null;
}> {
  const response = await apiClient.post(
    `/ai/situations/${situationId}/analyze`,
  );

  return response.data;
}