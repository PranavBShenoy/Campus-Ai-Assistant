'use client'

import React, { useEffect, useState } from 'react'
import { checkHealth, removeToken } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Settings2, Database, Key, Trash2, ShieldCheck, AlertCircle, Info, Github } from 'lucide-react'

export default function SettingsPage() {
  const [health, setHealth] = useState<{status: string, llm_configured: boolean, demo_mode: boolean, version: string} | null>(null)
  
  useEffect(() => {
    checkHealth().then(setHealth).catch(console.error)
    
  }, [])

  const handleSignOut = () => {
    removeToken()
    window.location.href = '/login'
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">System Settings</h1>
        <p className="text-gray-500 text-sm">Manage configuration and application state.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* LLM Config */}
        <Card>
          <CardHeader className="border-b bg-gray-50/50 pb-4">
            <CardTitle className="text-base flex items-center">
              <Key className="w-4 h-4 mr-2 text-gray-500" /> Language Model
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Status</span>
              {health ? (
                <Badge variant={health.llm_configured ? (health.demo_mode ? 'warning' : 'success') : 'danger'}>
                  {health.llm_configured ? (health.demo_mode ? 'Demo Mode' : 'Configured') : 'API Key Required'}
                </Badge>
              ) : (
                <span className="text-sm text-gray-400">Loading...</span>
              )}
            </div>
            
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 flex items-start">
              <Info className="w-5 h-5 text-blue-500 mr-2 shrink-0 mt-0.5" />
              <p className="text-xs text-blue-800">
                LLM configuration is managed on the backend. Edit <code className="bg-white px-1 py-0.5 rounded text-blue-900 font-mono border border-blue-200">backend/.env</code> to set your API keys (OpenRouter) and restart the server.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* RAG Settings (Display only) */}
        <Card>
          <CardHeader className="border-b bg-gray-50/50 pb-4">
            <CardTitle className="text-base flex items-center">
              <Database className="w-4 h-4 mr-2 text-gray-500" /> Retrieval Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500 mb-1">Chunk Size</p>
                <p className="font-medium">800 chars</p>
              </div>
              <div>
                <p className="text-gray-500 mb-1">Chunk Overlap</p>
                <p className="font-medium">150 chars</p>
              </div>
              <div>
                <p className="text-gray-500 mb-1">Retrieval Top-K</p>
                <p className="font-medium">5 documents</p>
              </div>
              <div>
                <p className="text-gray-500 mb-1">Vector DB</p>
                <p className="font-medium flex items-center">ChromaDB <ShieldCheck className="w-3 h-3 ml-1 text-emerald-500" /></p>
              </div>
            </div>
            <p className="text-[10px] text-gray-400 mt-4 pt-4 border-t">
              Note: System parameters are currently read-only. Modify backend configs to change.
            </p>
          </CardContent>
        </Card>

        {/* Account Management */}
        <Card className="md:col-span-2 border-red-100">
          <CardHeader className="border-b border-red-50 bg-red-50/30 pb-4">
            <CardTitle className="text-base flex items-center text-red-900">
              <Settings2 className="w-4 h-4 mr-2" /> Account Access
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-gray-900 mb-1">Authenticated account</p>
                <p className="text-xs text-gray-500 mt-2 max-w-md">
                  Your conversations, documents, and study plans are isolated by your signed-in user account.
                </p>
              </div>
              <Button variant="danger" onClick={handleSignOut} className="shrink-0">
                <Trash2 className="w-4 h-4 mr-2" /> Sign Out
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* About */}
        <Card className="md:col-span-2 shadow-none border-dashed bg-gray-50">
          <CardContent className="p-6 text-center">
            <div className="flex justify-center mb-3">
              <div className="bg-indigo-600 text-white p-2 rounded-lg">
                <Settings2 className="w-6 h-6" />
              </div>
            </div>
            <h3 className="font-bold text-gray-900 mb-1">CampusAI</h3>
            <p className="text-xs text-gray-500 mb-4">Version {health?.version || '1.0.0'} â€¢ Next.js 14 Frontend</p>
            <div className="flex justify-center">
              <Button variant="secondary" size="sm" className="bg-white">
                <Github className="w-4 h-4 mr-2" /> View Source
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

