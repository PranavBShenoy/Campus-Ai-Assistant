'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { DashboardStats } from '@/types'
import { getDashboardStats } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { Button } from '@/components/ui/Button'
import { FileText, MessageSquare, Calendar, MessageCircle, UploadCloud, ArrowRight, Activity, Clock } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true)
        const data = await getDashboardStats()
        setStats(data)
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data')
      } finally {
        setIsLoading(false)
      }
    }
    fetchStats()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-32 rounded-xl w-full" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-96 rounded-xl w-full" />
          <Skeleton className="h-96 rounded-xl w-full" />
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <div className="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mb-4">
          <Activity className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">Failed to load dashboard</h3>
        <p className="text-gray-500 mb-6">{error || 'Unknown error occurred'}</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    )
  }

  const statCards = [
    { title: 'Documents Indexed', value: stats.total_indexed_documents, icon: FileText, color: 'text-navy-600', bg: 'bg-navy-50' },
    { title: 'Questions Asked', value: stats.total_questions, icon: MessageSquare, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { title: 'Active Study Plans', value: stats.active_study_plans, icon: Calendar, color: 'text-purple-600', bg: 'bg-purple-50' },
    { title: 'Total Conversations', value: stats.total_conversations, icon: MessageCircle, color: 'text-blue-600', bg: 'bg-blue-50' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome Back</h1>
          <p className="text-gray-500">Here's what's happening with your academic progress.</p>
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <Button variant="secondary" onClick={() => router.push('/knowledge-base')} className="flex-1 sm:flex-none">
            <UploadCloud className="w-4 h-4 mr-2" />
            Upload
          </Button>
          <Button onClick={() => router.push('/assistant?newChat=true')} className="flex-1 sm:flex-none">
            Ask AI
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <Card key={i} className="border-none shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500 mb-1">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-900">{card.value}</p>
                </div>
                <div className={`p-3 rounded-xl ${card.bg} ${card.color}`}>
                  <card.icon className="w-6 h-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <div className="p-6 border-b border-gray-100 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Recent Conversations</h3>
            <Button variant="ghost" size="sm" onClick={() => router.push('/history')} className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50">
              View All <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
          <div className="p-0">
            {stats.recent_conversations.length > 0 ? (
              <ul className="divide-y divide-gray-100">
                {stats.recent_conversations.map((conv) => (
                  <li key={conv.id}>
                    <button 
                      onClick={() => router.push(`/assistant?conversation=${conv.id}`)}
                      className="w-full text-left px-6 py-4 hover:bg-gray-50 flex items-center justify-between transition-colors"
                    >
                      <div className="flex flex-col min-w-0 pr-4">
                        <p className="font-medium text-gray-900 truncate mb-1">{conv.title}</p>
                        <div className="flex items-center text-xs text-gray-500">
                          <Badge variant={conv.mode === 'academic_rag' ? 'info' : 'default'} className="mr-2 text-[10px] px-1.5 py-0">
                            {conv.mode === 'academic_rag' ? 'RAG' : 'Basic'}
                          </Badge>
                          <MessageCircle className="w-3 h-3 mr-1" /> {conv.message_count} messages
                        </div>
                      </div>
                      <div className="flex items-center text-xs text-gray-400 whitespace-nowrap">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatRelativeTime(conv.updated_at)}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-8 text-center text-gray-500 text-sm">
                No recent conversations.
                <div className="mt-4">
                  <Button variant="secondary" size="sm" onClick={() => router.push('/assistant?newChat=true')}>
                    Start a chat
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card>
          <div className="p-6 border-b border-gray-100 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Recent Documents</h3>
            <Button variant="ghost" size="sm" onClick={() => router.push('/knowledge-base')} className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50">
              View All <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
          <div className="p-0">
            {stats.recent_documents.length > 0 ? (
              <ul className="divide-y divide-gray-100">
                {stats.recent_documents.map((doc) => {
                  const isPdf = doc.filename.toLowerCase().endsWith('.pdf')
                  const isDocx = doc.filename.toLowerCase().endsWith('.docx')
                  return (
                    <li key={doc.id} className="px-6 py-4 flex items-center justify-between">
                      <div className="flex items-center min-w-0 pr-4">
                        <div className={`p-2 rounded-lg mr-4 flex-shrink-0 ${isPdf ? 'bg-red-50 text-red-500' : isDocx ? 'bg-blue-50 text-blue-500' : 'bg-gray-50 text-gray-500'}`}>
                          <FileText className="w-5 h-5" />
                        </div>
                        <div className="truncate">
                          <p className="font-medium text-gray-900 truncate mb-1" title={doc.original_filename}>{doc.original_filename}</p>
                          <div className="flex items-center text-xs text-gray-500">
                            {doc.status === 'indexed' ? (
                              <span className="text-emerald-600 font-medium">Indexed ({doc.chunk_count} chunks)</span>
                            ) : doc.status === 'processing' || doc.status === 'uploading' ? (
                              <span className="text-blue-600 font-medium flex items-center"><Activity className="w-3 h-3 mr-1 animate-pulse" /> Processing</span>
                            ) : (
                              <span className="text-red-500 font-medium">Failed</span>
                            )}
                            <span className="mx-2">•</span>
                            {formatRelativeTime(doc.upload_date)}
                          </div>
                        </div>
                      </div>
                    </li>
                  )
                })}
              </ul>
            ) : (
              <div className="p-8 text-center text-gray-500 text-sm">
                No indexed documents.
                <div className="mt-4">
                  <Button variant="secondary" size="sm" onClick={() => router.push('/knowledge-base')}>
                    Upload a file
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
