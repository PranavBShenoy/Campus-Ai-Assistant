'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { 
  MessageSquare, 
  BookOpen, 
  Calendar, 
  Settings, 
  BarChart,
  User,
  ChevronLeft,
  ChevronRight,
  LogOut
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { getCurrentUser, removeToken } from '@/lib/api'

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart },
  { name: 'AI Assistant', href: '/assistant', icon: MessageSquare },
  { name: 'Knowledge Base', href: '/knowledge-base', icon: BookOpen },
  { name: 'Study Planner', href: '/study-planner', icon: Calendar },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    getCurrentUser()
      .then(res => setUser(res))
      .catch(() => {
        // Ignored in sidebar
      })
  }, [])

  const handleLogout = () => {
    removeToken()
    router.replace('/login')
    router.refresh()
  }

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed)
  }

  return (
    <div 
      className={cn(
        "flex flex-col h-full bg-[#0F172A] border-r border-gray-800 transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-14 items-center justify-center border-b border-gray-800 px-4 flex-shrink-0">
        <BookOpen className="h-6 w-6 text-blue-500 flex-shrink-0" />
        {!isCollapsed && <span className="ml-3 text-lg font-bold text-white tracking-tight">CampusAI</span>}
      </div>

      <nav className="flex-1 overflow-y-auto py-4 space-y-1 px-2 scrollbar-hide">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== '/')
          return (
            <Link
              key={item.name}
              href={item.href}
              title={isCollapsed ? item.name : undefined}
              className={cn(
                "group flex items-center px-2.5 py-2.5 text-sm font-medium rounded-md transition-colors",
                isActive
                  ? "bg-blue-600/10 text-blue-500"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              )}
            >
              <item.icon className={cn("flex-shrink-0 h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
              {!isCollapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <div className={cn("flex items-center", isCollapsed ? "justify-center flex-col gap-4" : "justify-between")}>
          <div className="flex items-center overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
              <User className="w-4 h-4 text-gray-300" />
            </div>
            {!isCollapsed && (
              <div className="ml-3 truncate">
                <p className="text-sm font-medium text-white truncate">{user ? user.full_name : 'Loading...'}</p>
                <p className="text-xs text-gray-500 truncate">{user?.student_id ? `ID: ${user.student_id}` : 'Student'}</p>
              </div>
            )}
          </div>
          
          <div className={cn("flex items-center", isCollapsed ? "flex-col" : "gap-1")}>
            <button 
              onClick={handleLogout}
              title="Logout"
              className="p-1.5 rounded-md hover:bg-red-500/10 text-gray-400 hover:text-red-500 flex-shrink-0"
            >
              <LogOut className="w-4 h-4" />
            </button>
            <button 
              onClick={toggleCollapse}
              className="hidden md:flex p-1.5 rounded-md hover:bg-gray-800 text-gray-400 hover:text-white flex-shrink-0"
            >
              {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

