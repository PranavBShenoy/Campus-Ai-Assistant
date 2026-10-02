'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ConversationSummary } from '@/types'
import { getConversations, deleteConversation } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { EmptyState } from '@/components/ui/EmptyState'
import { Search, MessageCircle, Trash2, Clock, MessageSquare, History } from 'lucide-react'

export default function HistoryPage() {
  const router = useRouter()
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  const fetchConversations = async () => {
    try {
      setIsLoading(true)
      const data = await getConversations()
      setConversations(data)
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchConversations()
  }, [])

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await deleteConversation(id)
        await fetchConversations()
      } catch (err) {
        alert('Failed to delete')
      }
    }
  }

  const filteredConvs = conversations.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chat History</h1>
          <p className="text-gray-500 text-sm">Review past conversations with CampusAI</p>
        </div>
        <Button onClick={() => router.push('/assistant?newChat=true')}>
          <MessageSquare className="w-4 h-4 mr-2" /> New Chat
        </Button>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <Input 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search conversations..." 
          className="pl-10 h-12"
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1,2,3,4].map(i => <div key={i} className="h-20 bg-gray-100 animate-pulse rounded-xl" />)}
        </div>
      ) : filteredConvs.length > 0 ? (
        <div className="space-y-3">
          {filteredConvs.map(conv => (
            <Card 
              key={conv.id} 
              className="hover:border-indigo-300 transition-colors cursor-pointer group"
              onClick={() => router.push(`/assistant?conversation=${conv.id}`)}
            >
              <div className="p-5 flex items-center justify-between">
                <div className="flex items-start min-w-0 pr-4">
                  <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg mr-4 flex-shrink-0">
                    <MessageCircle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 truncate">{conv.title}</h3>
                    <div className="flex items-center text-xs text-gray-500 mt-1 space-x-3">
                      <Badge variant={conv.mode === 'academic_rag' ? 'info' : 'default'} className="text-[10px] py-0 px-1.5 h-4">
                        {conv.mode === 'academic_rag' ? 'RAG Mode' : 'Basic LLM'}
                      </Badge>
                      <span className="flex items-center"><MessageCircle className="w-3 h-3 mr-1" /> {conv.message_count} msgs</span>
                      <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> {formatRelativeTime(conv.updated_at)}</span>
                    </div>
                  </div>
                </div>
                <button 
                  onClick={(e) => handleDelete(conv.id, e)}
                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-md opacity-0 group-hover:opacity-100 transition-all focus:opacity-100"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="border-dashed shadow-none bg-gray-50">
          <EmptyState
            icon={History}
            title={searchQuery ? "No matching conversations found" : "No conversation history"}
            description={searchQuery ? "Try adjusting your search terms." : "Your past chats with CampusAI will appear here."}
          />
        </Card>
      )}
    </div>
  )
}
