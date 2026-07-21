export type User = {
  id: number;
  name: string;
  email: string;
  role: string;
  partner_id: number | null;
};
export type Partner = {
  id: number;
  name: string;
  slug: string;
  status: string;
  feed_type: string;
  default_language: string;
  default_territory: string;
  readiness_score: number;
};
export type Submission = {
  id: number;
  partner_id: number;
  format: string;
  filename: string;
  status: string;
  received_at: string;
  record_count: number;
  valid_records: number;
  invalid_records: number;
  retry_count: number;
  failure_reason?: string;
};
export type Issue = {
  id: number;
  code: string;
  category: string;
  severity: string;
  message: string;
  suggested_fix: string;
  row?: number;
  field?: string;
  content_id?: string;
  blocks_readiness: boolean;
};
