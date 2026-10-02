export type ChatMode = 'basic_llm' | 'academic_rag'

export interface SourceReference {
  document_id: string
  document_name: string
  excerpt: string
  page_number?: number
  chunk_id: string
  relevance_score: number
}

export interface ChatResponse {
  conversation_id: string
  message_id: string
  response: string
  sources: SourceReference[]
  mode: ChatMode
  processing_time_ms: number
  tokens_used?: number
  intent?: string
}

export interface ConversationSummary {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  mode: ChatMode
}

export interface MessageSchema {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: SourceReference[]
  mode: ChatMode
  created_at: string
}

export interface ConversationDetail {
  id: string
  title: string
  messages: MessageSchema[]
  created_at: string
  updated_at: string
}

export interface DocumentResponse {
  id: string
  filename: string
  original_filename: string
  file_type: string
  file_size: number
  status: 'uploading' | 'processing' | 'indexed' | 'failed' | 'deleted'
  error_message?: string
  chunk_count?: number
  upload_date: string
  processed_date?: string
}

export interface DocumentSearchResponse {
  results: SourceReference[]
}

export interface Subject {
  name: string
  topics: string[]
  exam_date: string  // YYYY-MM-DD
  exam_type?: 'mcq' | 'final_exam' | 'mid_sem' | 'unit_test' | 'internal_assessment' | 'practical' | 'general_study'
  difficulty: 'easy' | 'medium' | 'hard'
  priority: 'low' | 'medium' | 'high'
  current_level: 'beginner' | 'intermediate' | 'advanced'
}

export interface StudySession {
  id: string
  date: string
  subject: string
  topic: string
  duration_minutes: number
  session_type: 'study' | 'revision' | 'practice' | 'mock_test'
  is_completed: boolean
  notes?: string
}

export interface StudyPlanConstraints {
  daily_hours: number
  preferred_time: 'morning' | 'afternoon' | 'evening' | 'flexible'
  weekly_off_days: number[]
  break_frequency_minutes: number
  start_date: string
}

export interface GeneratePlanRequest {
  title: string
  constraints: StudyPlanConstraints
  subjects: Subject[]
}

export interface StudyPlanResponse {
  id: string
  title: string
  subjects: Subject[]
  sessions: StudySession[]
  constraints: StudyPlanConstraints
  start_date: string
  end_date: string
  created_at: string
  updated_at: string
  is_active: boolean
  total_sessions: number
  completed_sessions: number
}

export interface DashboardStats {
  total_documents: number
  total_indexed_documents: number
  total_questions: number
  active_study_plans: number
  total_conversations: number
  recent_conversations: ConversationSummary[]
  recent_documents: DocumentResponse[]
}

export interface EvaluationResult {
  question: string
  category: string
  basic_llm_response: string
  rag_response: string
  sources: SourceReference[]
  basic_latency_ms: number
  rag_latency_ms: number
  has_citations: boolean
  groundedness_score: number
  retrieval_count: number
}

export interface EvaluationRunResponse {
  run_id: string
  results: EvaluationResult[]
  avg_rag_latency: number
  avg_basic_latency: number
  avg_groundedness: number
  total_questions: number
  questions_with_citations: number
}

export interface EvaluationQuestion {
  id: string
  text: string
  category: string
  expected_has_answer: boolean
}
