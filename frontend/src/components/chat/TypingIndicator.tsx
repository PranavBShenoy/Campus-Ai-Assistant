import React from 'react'
import { Bot } from 'lucide-react'

export function TypingIndicator() {
  return (
    <div className="flex w-full justify-start mb-6">
      <div className="flex max-w-[85%] flex-row">
        <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mr-3 bg-gray-100 text-gray-700">
          <Bot className="w-5 h-5" />
        </div>
        <div className="flex flex-col justify-center">
          <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm flex items-center space-x-1 h-10">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          </div>
        </div>
      </div>
    </div>
  )
}
