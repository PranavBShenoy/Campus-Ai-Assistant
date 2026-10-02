"use client"
import React, { useEffect, useState } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { usePathname, useRouter } from 'next/navigation'
import { getCurrentUser, getToken } from '@/lib/api'

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [validatedPath, setValidatedPath] = useState<string | null>(null)
  const pathname = usePathname()
  const router = useRouter()
  
  const isAuthPage = pathname === '/login' || pathname === '/register'

  useEffect(() => {
    if (isAuthPage) {
      return
    }
    setValidatedPath(null)
    if (!getToken()) {
      router.replace('/login')
      return
    }
    getCurrentUser()
      .then(() => setValidatedPath(pathname))
      .catch(() => router.replace('/login'))
  }, [isAuthPage, pathname, router])
  
  if (isAuthPage) {
    return <main className="h-full bg-gray-50">{children}</main>
  }

  if (validatedPath !== pathname) {
    return <main className="h-screen bg-gray-50" />
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Mobile sidebar overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar container */}
      <div className={`fixed inset-y-0 left-0 z-50 transform md:relative md:translate-x-0 transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <Sidebar />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden w-full">
        <Header onOpenSidebar={() => setIsSidebarOpen(true)} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-4 md:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto h-full w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
