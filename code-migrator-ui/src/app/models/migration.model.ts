// Matches exactly what FastAPI returns
export interface MigrationRequest {
  code: string;
}

export interface MigrationResponse {
  success: boolean;
  source_version: string;
  target_version: string;
  language: string;
  original_code: string;
  migrated_code: string;
  score: number;
  review: Review;
  chunks_processed: number;
  error: string;
}

export interface Review {
  score: number;
  patterns_fixed: string[];
  patterns_missed: string[];
  bugs_introduced: string[];
  logic_preserved: boolean;
  overall_feedback: string;
}
