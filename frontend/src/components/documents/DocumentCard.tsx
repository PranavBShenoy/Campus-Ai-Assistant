import React from 'react'
import { DocumentResponse } from '@/types'
import { formatFileSize, formatDate } from '@/lib/utils'
import { Badge } from '@/components/ui/Badge'
import { FileText, File, Loader2, CheckCircle, XCircle, Trash2, RefreshCw } from 'lucide-react'

interface DocumentCardProps {
  document: DocumentResponse
  onDelete: (id: string) => void
  onRetry: (id: string) => void
}

export function DocumentCard({ document, onDelete, onRetry }: DocumentCardProps) {
  const isPdf = document.filename.toLowerCase().endsWith('.pdf')
  const isDocx = document.filename.toLowerCase().endsWith('.docx')
  
  const iconColor = isPdf ? 'text-red-500 bg-red-50' : isDocx ? 'text-blue-500 bg-blue-50' : 'text-gray-500 bg-gray-50'
  
  const statusConfig = {
    uploading: { color: 'warning', icon: Loader2, text: 'Uploading' },
    processing: { color: 'info', icon: Loader2, text: 'Processing' },
    indexed: { color: 'success', icon: CheckCircle, text: 'Indexed' },
    failed: { color: 'danger', icon: XCircle, text: 'Failed' },
    deleted: { color: 'default', icon: Trash2, text: 'Deleted' }
  }

  const status = statusConfig[document.status] || statusConfig.failed

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      onDelete(document.id)
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-col shadow-sm hover:shadow-md transition-shadow relative group">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2 rounded-lg ${iconColor}`}>
          {isPdf || isDocx ? <FileText className="w-6 h-6" /> : <File className="w-6 h-6" />}
        </div>
        <Badge variant={status.color as any} className="flex items-center space-x-1">
          {document.status === 'uploading' || document.status === 'processing' ? (
            <status.icon className="w-3 h-3 animate-spin mr-1" />
          ) : (
            <status.icon className="w-3 h-3 mr-1" />
          )}
          {status.text}
        </Badge>
      </div>
      
      <h4 className="text-sm font-medium text-gray-900 truncate mb-1" title={document.original_filename}>
        {document.original_filename}
      </h4>
      
      <div className="flex items-center text-xs text-gray-500 mb-4 space-x-2">
        <span>{formatFileSize(document.file_size)}</span>
        <span>•</span>
        <span>{formatDate(document.upload_date)}</span>
      </div>
      
      <div className="mt-auto pt-3 border-t border-gray-100 flex items-center justify-between">
        <div className="text-xs text-gray-500">
          {document.status === 'indexed' && document.chunk_count ? (
            <span>{document.chunk_count} chunks</span>
          ) : document.status === 'failed' ? (
            <button onClick={() => onRetry(document.id)} className="text-indigo-600 flex items-center" title="Retry indexing">
              <RefreshCw className="w-3 h-3 mr-1" /> Retry
            </button>
          ) : (
            <span>--</span>
          )}
        </div>
        <button 
          onClick={handleDelete}
          className="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-md hover:bg-red-50 opacity-0 group-hover:opacity-100 focus:opacity-100"
          title="Delete document"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
