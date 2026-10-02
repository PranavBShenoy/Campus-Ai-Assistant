import React, { useCallback, useState, useRef } from 'react'
import { UploadCloud, File, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { formatFileSize } from '@/lib/utils'

interface DropZoneProps {
  onUpload: (file: File) => Promise<void>
  isUploading: boolean
}

export function DropZone({ onUpload, isUploading }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]
      validateAndSetFile(file)
    }
  }, [])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0])
    }
  }, [])

  const validateAndSetFile = (file: File) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    if (!validTypes.includes(file.type) && !file.name.endsWith('.pdf') && !file.name.endsWith('.docx') && !file.name.endsWith('.txt')) {
      alert('Invalid file type. Please upload PDF, DOCX, or TXT.')
      return
    }
    if (file.size > 50 * 1024 * 1024) {
      alert('File size exceeds 50MB limit.')
      return
    }
    setSelectedFile(file)
  }

  const handleUploadClick = async () => {
    if (selectedFile) {
      await onUpload(selectedFile)
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div className="w-full">
      <div
        className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-colors cursor-pointer
          ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'}
          ${selectedFile ? 'border-indigo-300 bg-white' : ''}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !selectedFile && fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
        />
        
        {!selectedFile ? (
          <>
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-4 shadow-sm text-indigo-500">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Upload a Document</h3>
            <p className="text-sm text-gray-500 mb-4 text-center max-w-sm">
              Drag & Drop PDF, DOCX, or TXT files here or click to browse. Max file size: 50MB.
            </p>
          </>
        ) : (
          <div className="w-full max-w-md bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-center justify-between">
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className="p-2 bg-indigo-100 text-indigo-600 rounded-md shrink-0">
                <File className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate" title={selectedFile.name}>
                  {selectedFile.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
            <button 
              onClick={(e) => { e.stopPropagation(); setSelectedFile(null); if(fileInputRef.current) fileInputRef.current.value='' }}
              className="p-1 hover:bg-gray-200 rounded-md text-gray-500 shrink-0"
              disabled={isUploading}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
      
      {selectedFile && (
        <div className="mt-4 flex justify-end">
          <Button 
            onClick={handleUploadClick} 
            isLoading={isUploading}
            disabled={isUploading}
          >
            Upload {selectedFile.name}
          </Button>
        </div>
      )}
    </div>
  )
}
