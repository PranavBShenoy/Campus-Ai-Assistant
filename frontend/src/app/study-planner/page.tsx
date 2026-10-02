'use client'

import React, { useEffect, useState } from 'react'
import { useStudyPlan } from '@/hooks/useStudyPlan'
import { Subject, GeneratePlanRequest, StudyPlanConstraints } from '@/types'
import { WeeklyCalendar } from '@/components/study-planner/WeeklyCalendar'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { EmptyState } from '@/components/ui/EmptyState'
import { Calendar, Plus, Trash2, ArrowRight, Save, Send } from 'lucide-react'

export default function StudyPlannerPage() {
  const { plans, activePlan, setActivePlan, isLoading, isGenerating, error, loadPlans, generatePlan, modifyPlan, markSessionComplete } = useStudyPlan()
  
  const [isCreating, setIsCreating] = useState(false)
  const [step, setStep] = useState(1)
  
  // Form State
  const title = 'Study Plan'
  const startDate = new Date().toISOString().split('T')[0]
  const [constraints, setConstraints] = useState<StudyPlanConstraints>({
    daily_hours: 4,
    preferred_time: 'evening',
    weekly_off_days: [6],
    break_frequency_minutes: 90,
    start_date: new Date().toISOString().split('T')[0]
  })
  const [subjects, setSubjects] = useState<Subject[]>([])
  
  // New Subject Form State
  const [showSubjectForm, setShowSubjectForm] = useState(false)
  const [newSubject, setNewSubject] = useState<Subject>({
    name: '',
    topics: [],
    exam_date: '',
    exam_type: 'general_study',
    difficulty: 'medium',
    priority: 'medium',
    current_level: 'intermediate'
  })
  
  // Modify Plan State
  const [modifyInstruction, setModifyInstruction] = useState('')
  const [isModifying, setIsModifying] = useState(false)

  useEffect(() => {
    loadPlans()
  }, [loadPlans])

  const handleGenerate = async () => {
    if (subjects.length === 0) return alert('Add at least one subject')
    if (constraints.weekly_off_days.length === 7) return alert('Select at least one weekly study day')
    if (subjects.some(subject => subject.exam_date < startDate)) {
      return alert('Exam dates must be on or after the plan start date')
    }
    
    const request: GeneratePlanRequest = {
      title,
      constraints: { ...constraints, start_date: startDate },
      subjects
    }
    
    try {
      await generatePlan(request)
      setIsCreating(false)
      setStep(1)
    } catch {
      // The hook exposes the API error in the page.
    }
  }

  const handleAddSubject = () => {
    if (!newSubject.name || !newSubject.exam_date) return alert('Name and exam date required')
    if (newSubject.exam_date < startDate) return alert('Exam date must be on or after the plan start date')
    setSubjects([...subjects, { ...newSubject, topics: ['General study'] }])
    setShowSubjectForm(false)
    setNewSubject({ name: '', topics: [], exam_date: '', exam_type: 'general_study', difficulty: 'medium', priority: 'medium', current_level: 'intermediate' })
  }

  const handleModify = async () => {
    if (!modifyInstruction.trim() || !activePlan) return
    setIsModifying(true)
    try {
      await modifyPlan(activePlan.id, modifyInstruction)
      setModifyInstruction('')
    } catch {
      // The hook exposes the API error in the page.
    } finally {
      setIsModifying(false)
    }
  }

  const exportToCSV = () => {
    if (!activePlan) return
    let csv = 'Date,Subject,Topic,Duration (min),Type,Status\n'
    activePlan.sessions.forEach(s => {
      csv += `${s.date},"${s.subject}","${s.topic}",${s.duration_minutes},${s.session_type},${s.is_completed ? 'Completed' : 'Pending'}\n`
    })
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.setAttribute('hidden', '')
    a.setAttribute('href', url)
    a.setAttribute('download', `${activePlan.title.replace(/\s+/g, '_')}_plan.csv`)
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 animate-pulse">Loading study plans...</div>
  }

  if (isCreating) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Create Study Plan</h1>
            <p className="text-gray-500 text-sm">Step {step} of 3</p>
          </div>
          <Button variant="ghost" onClick={() => setIsCreating(false)}>Cancel</Button>
        </div>
        
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center w-full max-w-lg">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 1 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'}`}>1</div>
            <div className={`flex-1 h-1 mx-2 ${step >= 2 ? 'bg-indigo-600' : 'bg-gray-200'}`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 2 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'}`}>2</div>
            <div className={`flex-1 h-1 mx-2 ${step >= 3 ? 'bg-indigo-600' : 'bg-gray-200'}`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 3 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'}`}>3</div>
          </div>
        </div>

        <Card>
          <CardContent className="p-6">
            {step === 1 && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold border-b pb-2">Plan Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Daily Study Hours: {constraints.daily_hours}</label>
                    <input 
                      type="range" min="1" max="12" step="0.5" 
                      value={constraints.daily_hours} 
                      onChange={e => setConstraints({...constraints, daily_hours: parseFloat(e.target.value)})}
                      className="w-full"
                    />
                  </div>
                  
                  <Select label="Preferred Time" value={constraints.preferred_time} onChange={e => setConstraints({...constraints, preferred_time: e.target.value as any})}>
                    <option value="morning">Morning</option>
                    <option value="afternoon">Afternoon</option>
                    <option value="evening">Evening</option>
                    <option value="flexible">Flexible</option>
                  </Select>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Weekly Off Days</label>
                    <div className="flex flex-wrap gap-2">
                      {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map((day, dayIndex) => (
                        <label key={day} className="inline-flex items-center bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200 cursor-pointer hover:bg-gray-100">
                          <input 
                            type="checkbox" className="rounded text-indigo-600 focus:ring-indigo-500 mr-2"
                            checked={constraints.weekly_off_days.includes(dayIndex)}
                            onChange={(e) => {
                              const newDays = e.target.checked 
                                ? [...constraints.weekly_off_days, dayIndex]
                                : constraints.weekly_off_days.filter(d => d !== dayIndex)
                              setConstraints({...constraints, weekly_off_days: newDays})
                            }}
                          />
                          <span className="text-sm text-gray-700">{day.substring(0,3)}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex justify-end pt-4 border-t">
                  <Button onClick={() => setStep(2)}>Next Step <ArrowRight className="w-4 h-4 ml-2" /></Button>
                </div>
              </div>
            )}
            
            {step === 2 && (
              <div className="space-y-6">
                <div className="flex justify-between items-center border-b pb-2">
                  <h3 className="text-lg font-semibold">Subjects & Topics</h3>
                  <Button variant="secondary" size="sm" onClick={() => setShowSubjectForm(true)} disabled={showSubjectForm}>
                    <Plus className="w-4 h-4 mr-1" /> Add Subject
                  </Button>
                </div>
                
                {showSubjectForm && (
                  <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-6 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input label="Subject Name" placeholder="e.g. Database Management Systems" value={newSubject.name} onChange={e => setNewSubject({...newSubject, name: e.target.value})} />
                      <Input type="date" label="Exam Date" value={newSubject.exam_date} onChange={e => setNewSubject({...newSubject, exam_date: e.target.value})} />
                      <Select label="Exam Type (Optional)" value={newSubject.exam_type || 'general_study'} onChange={e => setNewSubject({...newSubject, exam_type: e.target.value as Subject['exam_type']})}>
                        <option value="general_study">General Study</option>
                        <option value="mcq">MCQ</option>
                        <option value="final_exam">Final Exam</option>
                        <option value="mid_sem">Mid-Sem / MSE</option>
                        <option value="unit_test">Unit Test</option>
                        <option value="internal_assessment">Internal Assessment</option>
                        <option value="practical">Practical</option>
                      </Select>
                    </div>
                    <div className="flex justify-end gap-2 pt-2">
                      <Button variant="ghost" size="sm" onClick={() => setShowSubjectForm(false)}>Cancel</Button>
                      <Button size="sm" onClick={handleAddSubject}>Save Subject</Button>
                    </div>
                  </div>
                )}
                
                <div className="space-y-3">
                  {subjects.length === 0 && !showSubjectForm && (
                    <div className="text-center py-8 text-gray-500">No subjects added yet.</div>
                  )}
                  {subjects.map((s, i) => (
                    <div key={i} className="flex items-center justify-between p-3 border rounded-lg bg-white">
                      <div>
                        <div className="flex items-center">
                          <h4 className="font-medium text-gray-900 mr-2">{s.name}</h4>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Exam: {s.exam_date} • {(s.exam_type || 'general_study').replaceAll('_', ' ')}</p>
                      </div>
                      <button onClick={() => setSubjects(subjects.filter((_, idx) => idx !== i))} className="text-gray-400 hover:text-red-500 p-2">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
                
                <div className="flex justify-between pt-4 border-t">
                  <Button variant="secondary" onClick={() => setStep(1)}>Back</Button>
                  <Button onClick={() => setStep(3)} disabled={subjects.length === 0 || showSubjectForm}>Next Step <ArrowRight className="w-4 h-4 ml-2" /></Button>
                </div>
              </div>
            )}
            
            {step === 3 && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold border-b pb-2">Review & Generate</h3>
                
                <div className="bg-indigo-50 p-4 rounded-xl border border-indigo-100">
                  <h4 className="font-semibold text-indigo-900 mb-2">{title}</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm text-indigo-800">
                    <div><strong>Start:</strong> {startDate}</div>
                    <div><strong>Pace:</strong> {constraints.daily_hours} hrs/day</div>
                    <div><strong>Subjects:</strong> {subjects.length}</div>
                    <div><strong>Off Days:</strong> {constraints.weekly_off_days.map(day => ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day]).join(', ') || 'None'}</div>
                  </div>
                </div>
                
                <div className="flex justify-between pt-4 border-t">
                  <Button variant="secondary" onClick={() => setStep(2)}>Back</Button>
                  <Button onClick={handleGenerate} isLoading={isGenerating}>Generate Study Plan <Save className="w-4 h-4 ml-2" /></Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!activePlan) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        {error && <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <EmptyState
          icon={Calendar}
          title="No Active Study Plan"
          description="Create a personalized study schedule based on your syllabus, exams, and learning preferences using our AI planner."
          action={<Button onClick={() => setIsCreating(true)}><Plus className="w-4 h-4 mr-2" /> Create Study Plan</Button>}
        />
      </div>
    )
  }

  // Active Plan View
  const completedCount = activePlan.sessions.filter(s => s.is_completed).length
  const progressPct = activePlan.sessions.length > 0 ? Math.round((completedCount / activePlan.sessions.length) * 100) : 0

  return (
    <div className="space-y-6">
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{activePlan.title}</h1>
          <p className="text-gray-500 text-sm">
            {activePlan.start_date} to {activePlan.end_date} • {activePlan.sessions.length} sessions
          </p>
        </div>
        <div className="flex gap-2">
          {plans.length > 1 && (
            <Select 
              value={activePlan.id} 
              onChange={e => setActivePlan(plans.find(p => p.id === e.target.value) || null)}
              className="w-48"
            >
              {plans.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
            </Select>
          )}
          <Button variant="secondary" onClick={exportToCSV}>Export CSV</Button>
          <Button onClick={() => setIsCreating(true)}><Plus className="w-4 h-4 mr-2" /> New</Button>
        </div>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="p-4 flex items-center gap-4">
          <div className="flex-1">
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium text-gray-700">Overall Progress</span>
              <span className="font-bold text-indigo-600">{progressPct}%</span>
            </div>
            <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-600 transition-all duration-500" style={{ width: `${progressPct}%` }} />
            </div>
          </div>
          <div className="text-xs text-gray-500 whitespace-nowrap bg-gray-50 px-3 py-2 rounded-lg border">
            {completedCount} / {activePlan.sessions.length} done
          </div>
        </CardContent>
      </Card>

      {/* Calendar View */}
      <Card>
        <CardHeader className="border-b">
          <CardTitle>Schedule</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <WeeklyCalendar 
            sessions={activePlan.sessions} 
            startDate={activePlan.start_date} 
            onToggleComplete={(id, completed) => markSessionComplete(activePlan.id, id, completed)} 
          />
        </CardContent>
      </Card>

      {/* Modify Plan */}
      <Card>
        <CardHeader className="border-b bg-gray-50/50">
          <CardTitle className="text-base">Modify Plan with AI</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <p className="text-sm text-gray-500 mb-4">
            Need adjustments? Tell the AI what changed (e.g., "I'm sick today, push everything back", "I only have 2 hours on Fridays").
          </p>
          <div className="flex gap-3">
            <Input 
              value={modifyInstruction} 
              onChange={e => setModifyInstruction(e.target.value)} 
              placeholder="Enter instructions..." 
              className="flex-1"
              onKeyDown={e => { if(e.key==='Enter') handleModify() }}
            />
            <Button onClick={handleModify} isLoading={isModifying} disabled={!modifyInstruction.trim()}>
              <Send className="w-4 h-4 mr-2" /> Apply
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
