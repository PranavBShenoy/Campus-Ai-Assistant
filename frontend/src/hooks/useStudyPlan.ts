import { useState, useCallback } from 'react'
import { StudyPlanResponse, GeneratePlanRequest } from '@/types'
import { getStudyPlans, generateStudyPlan, modifyStudyPlan, updateSession } from '@/lib/api'

export function useStudyPlan() {
  const [plans, setPlans] = useState<StudyPlanResponse[]>([])
  const [activePlan, setActivePlan] = useState<StudyPlanResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadPlans = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await getStudyPlans()
      setPlans(data)
      setActivePlan(current => current || data.find(p => p.is_active) || data[0] || null)
    } catch (err: any) {
      setError(err.message || 'Failed to load study plans')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const generatePlan = useCallback(async (data: GeneratePlanRequest) => {
    try {
      setIsGenerating(true)
      setError(null)
      const newPlan = await generateStudyPlan(data)
      setPlans(prev => [...prev, newPlan])
      setActivePlan(newPlan)
    } catch (err: any) {
      setError(err.message || 'Failed to generate study plan')
      throw err
    } finally {
      setIsGenerating(false)
    }
  }, [])

  const modifyPlan = useCallback(async (planId: string, instruction: string) => {
    try {
      setError(null)
      const updatedPlan = await modifyStudyPlan(planId, instruction)
      setPlans(prev => prev.map(p => p.id === planId ? updatedPlan : p))
      if (activePlan?.id === planId) {
        setActivePlan(updatedPlan)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to modify study plan')
      throw err
    }
  }, [activePlan])

  const markSessionComplete = useCallback(async (planId: string, sessionId: string, completed: boolean) => {
    try {
      setError(null)
      const updatedPlan = await updateSession(planId, sessionId, { is_completed: completed })
      setPlans(prev => prev.map(p => p.id === planId ? updatedPlan : p))
      if (activePlan?.id === planId) {
        setActivePlan(updatedPlan)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update session')
    }
  }, [activePlan])

  return { plans, activePlan, setActivePlan, isLoading, isGenerating, error, loadPlans, generatePlan, modifyPlan, markSessionComplete }
}
