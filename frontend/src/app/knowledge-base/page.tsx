'use client'

import React, { useEffect, useState } from 'react'
import { useDocuments } from '@/hooks/useDocuments'
import { searchDocuments } from '@/lib/api'
import { DocumentSearchResponse, SourceReference } from '@/types'
import { DropZone } from '@/components/documents/DropZone'
import { DocumentCard } from '@/components/documents/DocumentCard'
import { SourceCard } from '@/components/chat/SourceCard'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { EmptyState } from '@/components/ui/EmptyState'
import { Toast } from '@/components/ui/Toast'
import { Skeleton } from '@/components/ui/Skeleton'
import { BookOpen, Search, Filter } from 'lucide-react'

export default function KnowledgeBasePage() {
  const { documents, isLoading, isUploading, error, loadDocuments, uploadDocument, deleteDocument, reindexDocument } = useDocuments()
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SourceReference[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  // Polling for document status
  useEffect(() => {
    const hasProcessingDocs = documents.some(d => d.status === 'uploading' || d.status === 'processing')
    if (hasProcessingDocs) {
      const interval = setInterval(() => {
        loadDocuments()
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [documents, loadDocuments])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    
    try {
      setIsSearching(true)
      setSearchError(null)
      const res = await searchDocuments(searchQuery)
      setSearchResults(res.results || [])
    } catch (err: any) {
      setSearchError(err.message || 'Search failed')
    } finally {
      setIsSearching(false)
    }
  }

  const activeDocs = documents.filter(d => d.status !== 'deleted')

  return (
    <div className="space-y-8">
      {error && <Toast message={error} type="error" onClose={() => {}} />}
      
      <div className="flex flex-col md:flex-row gap-8">
        {/* Left Column: Upload */}
        <div className="w-full md:w-1/3 flex flex-col space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">Knowledge Base</h1>
            <p className="text-gray-500 text-sm">Upload documents to build your AI's context.</p>
          </div>
          
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
            <DropZone onUpload={uploadDocument} isUploading={isUploading} />
          </div>
        </div>

        {/* Right Column: Search & List */}
        <div className="w-full md:w-2/3 flex flex-col space-y-6">
          {/* Search Bar */}
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
            <form onSubmit={handleSearch} className="flex space-x-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search across indexed documents..." 
                  className="pl-9"
                />
              </div>
              <Button type="submit" isLoading={isSearching} disabled={!searchQuery.trim()}>
                Search
              </Button>
            </form>
            
            {searchError && <p className="text-sm text-red-500 mt-2">{searchError}</p>}
            
            {searchResults.length > 0 && (
              <div className="mt-4 space-y-3">
                <h4 className="text-sm font-semibold text-gray-700">Top Matches</h4>
                {searchResults.map((result, i) => (
                  <SourceCard key={i} source={result} />
                ))}
                <div className="flex justify-center mt-2">
                  <Button variant="ghost" size="sm" onClick={() => setSearchResults([])}>Clear Results</Button>
                </div>
              </div>
            )}
          </div>

          {/* Documents List */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Indexed Documents ({activeDocs.length})</h3>
              <Button variant="ghost" size="sm" onClick={() => loadDocuments()} className="text-gray-500">
                Refresh
              </Button>
            </div>
            
            {isLoading && activeDocs.length === 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full rounded-xl" />)}
              </div>
            ) : activeDocs.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {activeDocs.map(doc => (
                  <DocumentCard key={doc.id} document={doc} onDelete={deleteDocument} onRetry={reindexDocument} />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-dashed border-gray-300">
                <EmptyState
                  icon={BookOpen}
                  title="No documents yet"
                  description="Upload your first academic document (syllabus, notes, rules) to start building your knowledge base."
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
