import React from 'react'
import { StudySession } from '@/types'
import { SessionCard } from './SessionCard'
import { format, parseISO, eachDayOfInterval, startOfWeek, endOfWeek, isSameDay, max as maxDate } from 'date-fns'

interface WeeklyCalendarProps {
  sessions: StudySession[]
  startDate: string
  onToggleComplete: (id: string, completed: boolean) => void
}

export function WeeklyCalendar({ sessions, startDate, onToggleComplete }: WeeklyCalendarProps) {
  const start = startOfWeek(parseISO(startDate), { weekStartsOn: 1 }) // Monday
  const lastSession = sessions.length ? maxDate(sessions.map(s => parseISO(s.date))) : parseISO(startDate)
  const days = eachDayOfInterval({ start, end: endOfWeek(lastSession, { weekStartsOn: 1 }) })

  return (
    <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
      {days.map(day => {
        const daySessions = sessions.filter(s => isSameDay(parseISO(s.date), day))
        
        return (
          <div key={day.toISOString()} className="flex flex-col">
            <div className="text-center py-2 mb-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-xs font-medium text-gray-500 uppercase">{format(day, 'EEE')}</div>
              <div className="text-lg font-semibold text-gray-900">{format(day, 'd')}</div>
            </div>
            
            <div className="flex flex-col space-y-3 flex-1">
              {daySessions.length === 0 ? (
                <div className="text-center text-xs text-gray-400 py-4 border border-dashed border-gray-200 rounded-lg">
                  No sessions
                </div>
              ) : (
                daySessions.map(session => (
                  <SessionCard key={session.id} session={session} onToggleComplete={onToggleComplete} />
                ))
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
