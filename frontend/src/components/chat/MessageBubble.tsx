import React, { useState } from 'react'
import { MessageSchema } from '@/types'
import { formatRelativeTime } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'
import { SourceCard } from './SourceCard'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ChevronDown, ChevronRight, User, Bot } from 'lucide-react'

interface MessageBubbleProps {
  message: MessageSchema
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [sourcesExpanded, setSourcesExpanded] = useState(false)

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'ml-3 bg-indigo-100 text-indigo-700' : 'mr-3 bg-gray-100 text-gray-700'}`}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </div>
        
        <div className="flex flex-col">
          <div className="flex items-center mb-1 space-x-2">
            <span className="text-xs text-gray-500">
              {isUser ? 'You' : 'CampusAI'} • {formatRelativeTime(message.created_at)}
            </span>
            {!isUser && (
              <Badge variant={message.mode === 'academic_rag' ? 'info' : 'default'} className="text-[10px] px-1.5 py-0">
                {message.mode === 'academic_rag' ? 'Academic RAG' : 'Basic LLM'}
              </Badge>
            )}
          </div>
          
          <div className={`relative px-4 py-3 rounded-2xl ${isUser ? 'bg-indigo-600 text-white rounded-tr-sm' : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm shadow-sm'}`}>
            <div className={`prose prose-sm max-w-none ${isUser ? 'prose-invert text-white' : ''}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
          
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-2 w-full max-w-2xl">
              <button 
                onClick={() => setSourcesExpanded(!sourcesExpanded)}
                className="flex items-center text-xs text-gray-500 hover:text-gray-700 font-medium transition-colors"
              >
                {sourcesExpanded ? <ChevronDown className="w-3 h-3 mr-1" /> : <ChevronRight className="w-3 h-3 mr-1" />}
                Sources ({message.sources.length})
              </button>
              
              {sourcesExpanded && (
                <div className="mt-2 space-y-2">
                  {message.sources.map((source, i) => (
                    <SourceCard key={`${source.document_id}-${source.chunk_id}-${i}`} source={source} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
