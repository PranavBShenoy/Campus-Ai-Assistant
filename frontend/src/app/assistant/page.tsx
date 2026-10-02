'use client'
import { Suspense } from 'react'

import React, { useEffect, useState, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useChat } from '@/hooks/useChat'
import { ChatMode, ConversationSummary } from '@/types'
import { getConversations, deleteConversation } from '@/lib/api'
import { SUGGESTED_QUESTIONS } from '@/lib/constants'
import { MessageBubble } from '@/components/chat/MessageBubble'
import { TypingIndicator } from '@/components/chat/TypingIndicator'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { Toast } from '@/components/ui/Toast'
import { Textarea } from '@/components/ui/Textarea'
import { Send, GraduationCap, MessageSquare, Plus, Trash2, Hash } from 'lucide-react'

function AssistantContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const chatBottomRef = useRef<HTMLDivElement>(null)
  
  const { messages, isLoading, error, conversationId, sendMessage, clearChat, loadConversation } = useChat()
  const [mode, setMode] = useState<ChatMode>('academic_rag')
  const [inputText, setInputText] = useState('')
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [sidebarError, setSidebarError] = useState<string | null>(null)

  const loadConvHistory = async () => {
    try {
      const data = await getConversations()
      setConversations(data)
    } catch (err: any) {
      console.error(err)
    }
  }

  useEffect(() => {
    loadConvHistory()
    
    const newChat = searchParams.get('newChat')
    const convId = searchParams.get('conversation')
    
    if (newChat === 'true') {
      clearChat()
      router.replace('/assistant')
    } else if (convId) {
      loadConversation(convId).catch(() => {
        setSidebarError('Failed to load conversation')
      })
    }
  }, [searchParams, clearChat, loadConversation, router])

  useEffect(() => {
    if (messages.length > 0) {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isLoading])

  const handleSend = async () => {
    const text = inputText.trim()
    if (!text || isLoading) return
    
    setInputText('')
    try {
      await sendMessage(text, mode)
      loadConvHistory() // Refresh history to update titles
    } catch (err) {
      // Error handled by hook
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (window.confirm('Delete this conversation?')) {
      try {
        await deleteConversation(id)
        if (id === conversationId) {
          clearChat()
          router.replace('/assistant')
        }
        await loadConvHistory()
      } catch (err) {
        setSidebarError('Failed to delete conversation')
      }
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] -m-4 md:-m-6 lg:-m-8 bg-white border-t border-gray-200">
      {/* Sidebar for chat history */}
      <div className="hidden md:flex flex-col w-64 border-r border-gray-200 bg-gray-50 h-full">
        <div className="p-4 border-b border-gray-200">
          <Button 
            className="w-full justify-start" 
            variant="secondary"
            onClick={() => {
              clearChat()
              router.push('/assistant?newChat=true')
            }}
          >
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-custom p-3 space-y-1">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Recent Chats</h3>
          {conversations.map(conv => (
            <div 
              key={conv.id}
              onClick={() => router.push(`/assistant?conversation=${conv.id}`)}
              className={`flex items-center justify-between p-2 rounded-lg cursor-pointer group transition-colors ${
                conversationId === conv.id ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-200 text-gray-700'
              }`}
            >
              <div className="flex items-center overflow-hidden mr-2">
                <Hash className={`w-4 h-4 mr-2 flex-shrink-0 ${conversationId === conv.id ? 'text-indigo-500' : 'text-gray-400'}`} />
                <span className="text-sm truncate font-medium">{conv.title}</span>
              </div>
              <button 
                onClick={(e) => handleDeleteConversation(conv.id, e)}
                className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          {conversations.length === 0 && (
            <p className="text-xs text-gray-500 text-center py-4">No recent chats</p>
          )}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {error && <Toast message={error} type="error" onClose={() => {}} />}
        {sidebarError && <Toast message={sidebarError} type="error" onClose={() => setSidebarError(null)} />}

        {/* Header/Mode Selector */}
        <div className="h-14 border-b border-gray-200 flex items-center justify-center bg-white z-10 shrink-0">
          <div className="flex bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setMode('basic_llm')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                mode === 'basic_llm' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Basic LLM
            </button>
            <button
              onClick={() => setMode('academic_rag')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                mode === 'academic_rag' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Academic RAG
            </button>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 scrollbar-custom bg-gray-50/50">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto">
              <EmptyState
                icon={GraduationCap}
                title="How can I help you today?"
                description={mode === 'academic_rag' ? 'Ask questions about your uploaded academic documents, syllabus, rules, and course material.' : 'General AI chat mode. Does not search your documents.'}
              />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mt-8">
                {SUGGESTED_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => { setInputText(q); }}
                    className="text-left p-4 rounded-xl border border-gray-200 bg-white hover:border-indigo-300 hover:shadow-sm transition-all group"
                  >
                    <p className="text-sm text-gray-700 group-hover:text-indigo-700 font-medium">{q}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto w-full">
              {messages.map(msg => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isLoading && <TypingIndicator />}
              <div ref={chatBottomRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-200">
          <div className="max-w-4xl mx-auto relative flex items-end shadow-sm border border-gray-300 rounded-xl bg-white overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-shadow">
            <Textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question..."
              className="border-0 focus:ring-0 resize-none py-3 px-4 min-h-[52px] max-h-[160px] shadow-none bg-transparent"
              autoResize
              disabled={isLoading}
            />
            <div className="p-2 shrink-0">
              <Button 
                onClick={handleSend} 
                disabled={!inputText.trim() || isLoading}
                className="w-10 h-10 rounded-lg p-0 flex items-center justify-center"
              >
                <Send className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
          <div className="max-w-4xl mx-auto mt-2 text-center">
            <p className="text-[10px] text-gray-400">
              CampusAI can make mistakes. Verify important academic information. 
              {mode === 'academic_rag' && ' Answers are based on your indexed documents.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AssistantPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AssistantContent />
    </Suspense>
  )
}
