import { useState, useCallback } from 'react'
import { ChatMode, MessageSchema } from '@/types'
import { sendMessage as apiSendMessage, getConversation } from '@/lib/api'
import { v4 as uuidv4 } from 'uuid'

export function useChat() {
  const [messages, setMessages] = useState<MessageSchema[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | undefined>()

  const sendMessage = useCallback(async (text: string, mode: ChatMode) => {
    try {
      setIsLoading(true)
      setError(null)
      
      const userMessage: MessageSchema = {
        id: uuidv4(),
        role: 'user',
        content: text,
        mode,
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])

      const response = await apiSendMessage(text, mode, conversationId)
      
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id)
      }

      const assistantMessage: MessageSchema = {
        id: response.message_id || uuidv4(),
        role: 'assistant',
        content: response.response,
        sources: response.sources,
        mode: response.mode,
        created_at: new Date().toISOString()
      }
      
      setMessages(prev => [...prev, assistantMessage])
    } catch (err: any) {
      setError(err.message || 'Failed to send message')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [conversationId])

  const clearChat = useCallback(() => {
    setMessages([])
    setConversationId(undefined)
    setError(null)
  }, [])

  const loadConversation = useCallback(async (id: string) => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await getConversation(id)
      setMessages(data.messages || [])
      setConversationId(data.id)
    } catch (err: any) {
      setError(err.message || 'Failed to load conversation')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  return { messages, isLoading, error, conversationId, sendMessage, clearChat, loadConversation }
}
