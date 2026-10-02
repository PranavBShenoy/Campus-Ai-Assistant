import { useState, useCallback } from 'react'
import { DocumentResponse } from '@/types'
import { getDocuments, uploadDocument as apiUpload, deleteDocument as apiDelete, reindexDocument as apiReindex } from '@/lib/api'

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadDocuments = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const docs = await getDocuments()
      setDocuments(docs)
    } catch (err: any) {
      setError(err.message || 'Failed to load documents')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const uploadDocument = useCallback(async (file: File) => {
    try {
      setIsUploading(true)
      setError(null)
      await apiUpload(file)
      await loadDocuments()
    } catch (err: any) {
      setError(err.message || 'Failed to upload document')
      throw err
    } finally {
      setIsUploading(false)
    }
  }, [loadDocuments])

  const deleteDocument = useCallback(async (id: string) => {
    try {
      setError(null)
      await apiDelete(id)
      await loadDocuments()
    } catch (err: any) {
      setError(err.message || 'Failed to delete document')
      throw err
    }
  }, [loadDocuments])

  const reindexDocument = useCallback(async (id: string) => {
    try {
      setError(null)
      await apiReindex(id)
      await loadDocuments()
    } catch (err: any) {
      setError(err.message || 'Failed to retry document')
      throw err
    }
  }, [loadDocuments])

  return { documents, isLoading, isUploading, error, loadDocuments, uploadDocument, deleteDocument, reindexDocument }
}
