import {
  ChatMode,
  ChatResponse,
  ConversationSummary,
  ConversationDetail,
  DocumentResponse,
  DocumentSearchResponse,
  StudyPlanResponse,
  GeneratePlanRequest,
  StudySession,
  EvaluationRunResponse,
  DashboardStats,
  EvaluationQuestion
} from '@/types'

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

export function setToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token)
    document.cookie = `access_token=${encodeURIComponent(token)}; Path=/; SameSite=Lax`
  }
}

export function removeToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token')
    document.cookie = 'access_token=; Path=/; Max-Age=0; SameSite=Lax'
  }
}

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`
  const headers = new Headers(options.headers || {})
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  const token = getToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let res: Response
  try {
    res = await fetch(url, { ...options, headers, signal: options.signal || AbortSignal.timeout(120000) })
  } catch {
    throw new Error('CampusAI is unavailable. Check that the backend is running and try again.')
  }
  
  if (res.status === 401) {
    removeToken()
    if (typeof window !== 'undefined' && window.location.pathname !== '/login' && window.location.pathname !== '/register') {
      window.location.href = '/login'
    }
  }
  
  if (!res.ok) {
    let errorMessage = res.status >= 500
      ? 'CampusAI could not complete the request. Please try again.'
      : 'Please check your information and try again.'
    try {
      const errorBody = await res.json()
      if (errorBody.detail) {
        if (typeof errorBody.detail === 'string') {
          errorMessage = errorBody.detail
        } else if (Array.isArray(errorBody.detail)) {
          errorMessage = 'Please check the entered values and try again.'
        } else {
          errorMessage = JSON.stringify(errorBody.detail)
        }
      } else if (errorBody.message) {
        errorMessage = typeof errorBody.message === 'string'
          ? errorBody.message
          : JSON.stringify(errorBody.message)
      }
    } catch (e) {
      // Ignored if JSON parsing fails
    }
    throw new Error(errorMessage)
  }
  return res.json()
}

export async function checkHealth(): Promise<{status: string, llm_configured: boolean, demo_mode: boolean, version: string}> {
  return fetchAPI('/api/health')
}

// Auth API
export async function registerUser(data: any): Promise<any> {
  return fetchAPI('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function loginUser(email: string, password: string): Promise<any> {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)
  
  return fetchAPI('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData.toString()
  })
}

export async function getCurrentUser(): Promise<any> {
  return fetchAPI('/api/auth/me')
}

export async function sendMessage(message: string, mode: ChatMode, conversationId?: string): Promise<ChatResponse> {
  return fetchAPI('/api/chat/', {
    method: 'POST',
    body: JSON.stringify({
      message,
      mode,
      conversation_id: conversationId,
      session_id: '' // Deprecated by user_id but kept for schema compatibility
    })
  })
}

export async function getConversations(): Promise<ConversationSummary[]> {
  return fetchAPI(`/api/chat/conversations`)
}

export async function getConversation(id: string): Promise<ConversationDetail> {
  return fetchAPI(`/api/chat/conversations/${id}`)
}

export async function deleteConversation(id: string): Promise<void> {
  return fetchAPI(`/api/chat/conversations/${id}`, { method: 'DELETE' })
}

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const formData = new FormData()
  formData.append('file', file)
  return fetchAPI('/api/documents/upload', {
    method: 'POST',
    body: formData
  })
}

export async function getDocuments(): Promise<DocumentResponse[]> {
  return fetchAPI('/api/documents/')
}

export async function deleteDocument(id: string): Promise<void> {
  return fetchAPI(`/api/documents/${id}`, { method: 'DELETE' })
}

export async function reindexDocument(id: string): Promise<DocumentResponse> {
  return fetchAPI(`/api/documents/${id}/reindex`, { method: 'POST' })
}

export async function searchDocuments(query: string, topK: number = 5): Promise<DocumentSearchResponse> {
  return fetchAPI('/api/documents/search', {
    method: 'POST',
    body: JSON.stringify({ query, top_k: topK })
  })
}

export async function generateStudyPlan(data: GeneratePlanRequest): Promise<StudyPlanResponse> {
  return fetchAPI('/api/study-plans/generate', {
    method: 'POST',
    body: JSON.stringify({ ...data, session_id: '' })
  })
}

export async function getStudyPlans(): Promise<StudyPlanResponse[]> {
  return fetchAPI(`/api/study-plans/`)
}

export async function getStudyPlan(id: string): Promise<StudyPlanResponse> {
  return fetchAPI(`/api/study-plans/${id}`)
}

export async function modifyStudyPlan(planId: string, instruction: string): Promise<StudyPlanResponse> {
  return fetchAPI(`/api/study-plans/${planId}/modify`, {
    method: 'POST',
    body: JSON.stringify({ instruction })
  })
}

export async function updateSession(planId: string, sessionId: string, updates: Partial<StudySession>): Promise<StudyPlanResponse> {
  return fetchAPI(`/api/study-plans/${planId}/sessions/${sessionId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates)
  })
}

export async function runEvaluation(questions: EvaluationQuestion[]): Promise<EvaluationRunResponse> {
  return fetchAPI('/api/evaluation/run', {
    method: 'POST',
    body: JSON.stringify({
      questions: questions.map(({ text, category, expected_has_answer }) => ({
        question: text,
        category,
        expected_has_answer
      })),
      session_id: null
    })
  })
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchAPI(`/api/dashboard/stats`)
}
