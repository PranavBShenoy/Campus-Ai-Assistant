"use client";
import React, { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { Menu } from 'lucide-react'
import { checkHealth } from '@/lib/api'
import { Badge } from '@/components/ui/Badge'

interface HeaderProps {
  onOpenSidebar: () => void
}

export function Header({ onOpenSidebar }: HeaderProps) {
  const pathname = usePathname()
  const [health, setHealth] = useState<{status: string, llm_configured: boolean, demo_mode: boolean} | null>(null)

  useEffect(() => {
    checkHealth().then(setHealth).catch(console.error)
  }, [])

  const routeTitles: Record<string, string> = {
    '/dashboard': 'Dashboard',
    '/assistant': 'AI Assistant',
    '/knowledge-base': 'Knowledge Base',
    '/study-planner': 'Study Planner',
    '/history': 'History',
    '/evaluation': 'RAG Evaluation',
    '/settings': 'Settings',
  }

  const title = routeTitles[pathname] || 'CampusAI'

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 sm:px-6 lg:px-8 shrink-0">
      <div className="flex items-center">
        <button
          onClick={onOpenSidebar}
          className="mr-4 md:hidden p-2 -ml-2 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700"
        >
          <Menu className="w-6 h-6" />
        </button>
        <h1 className="text-xl font-bold text-gray-900">{title}</h1>
      </div>

      <div className="flex items-center">
        {health && (
          <Badge 
            variant={!health.llm_configured ? 'danger' : health.demo_mode ? 'warning' : 'success'}
            className="hidden sm:flex"
          >
            {!health.llm_configured ? 'API Key Required' : health.demo_mode ? 'Demo Mode' : 'AI Ready'}
          </Badge>
        )}
      </div>
    </header>
  )
}