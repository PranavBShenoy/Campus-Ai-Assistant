import React, { useState } from 'react'
import { SourceReference } from '@/types'
import { ChevronDown, ChevronUp, FileText } from 'lucide-react'

interface SourceCardProps {
  source: SourceReference
}

export function SourceCard({ source }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false)
  
  // Convert score to percentage and color
  const scorePct = Math.round(source.relevance_score * 100)
  const scoreColor = source.relevance_score > 0.7 ? 'bg-emerald-500' : source.relevance_score > 0.4 ? 'bg-amber-500' : 'bg-red-500'

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white mt-2">
      <div 
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-3 overflow-hidden">
          <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
          <span className="text-sm font-medium text-gray-700 truncate">{source.document_name}</span>
          {source.page_number && (
            <span className="text-xs text-gray-500 flex-shrink-0">Page {source.page_number}</span>
          )}
        </div>
        <div className="flex items-center space-x-3 flex-shrink-0 ml-4">
          <div className="flex items-center space-x-1.5 w-24">
            <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
              <div className={`h-full ${scoreColor}`} style={{ width: `${scorePct}%` }} />
            </div>
            <span className="text-xs text-gray-500 w-8">{scorePct}%</span>
          </div>
          {expanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
        </div>
      </div>
      
      {expanded && (
        <div className="p-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-600 font-mono whitespace-pre-wrap">
          {source.excerpt}
        </div>
      )}
    </div>
  )
}
