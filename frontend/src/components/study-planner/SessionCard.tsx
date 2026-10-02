import React from 'react'
import { StudySession } from '@/types'
import { Badge } from '@/components/ui/Badge'
import { Clock, CheckSquare, Square } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SessionCardProps {
  session: StudySession
  onToggleComplete: (id: string, completed: boolean) => void
}

export function SessionCard({ session, onToggleComplete }: SessionCardProps) {
  const typeConfig = {
    study: { color: 'info', label: 'Study' },
    revision: { color: 'purple', label: 'Revision' },
    practice: { color: 'warning', label: 'Practice' },
    mock_test: { color: 'danger', label: 'Mock Test' }
  }

  const config = typeConfig[session.session_type] || typeConfig.study

  return (
    <div className={cn(
      'p-3 rounded-lg border text-left transition-colors cursor-pointer group',
      session.is_completed ? 'bg-gray-50 border-gray-200 opacity-60' : 'bg-white border-gray-200 hover:border-indigo-300 shadow-sm'
    )}
    onClick={() => onToggleComplete(session.id, !session.is_completed)}>
      <div className="flex items-start justify-between mb-2">
        <Badge variant={config.color as any} className="text-[10px] px-1.5 py-0 leading-tight">
          {config.label}
        </Badge>
        <button className="text-gray-400 group-hover:text-indigo-600 transition-colors">
          {session.is_completed ? (
            <CheckSquare className="w-4 h-4 text-emerald-500" />
          ) : (
            <Square className="w-4 h-4" />
          )}
        </button>
      </div>
      
      <h4 className={cn('text-sm font-semibold truncate', session.is_completed ? 'line-through text-gray-500' : 'text-gray-900')}>
        {session.subject}
      </h4>
      <p className="text-xs text-gray-600 truncate mb-2" title={session.topic}>
        {session.topic}
      </p>
      
      <div className="flex items-center text-xs text-gray-500 font-medium">
        <Clock className="w-3 h-3 mr-1" />
        {session.duration_minutes}m
      </div>
    </div>
  )
}
