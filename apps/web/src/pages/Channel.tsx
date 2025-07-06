import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import { Send, Paperclip, Smile } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface Message {
  id: string
  content: string
  user: {
    id: string
    username: string
    avatar?: string
  }
  created_at: string
  reactions: Reaction[]
  thread?: Message[]
}

interface Reaction {
  id: string
  emoji: string
  count: number
  users: string[]
}

const Channel = () => {
  const { channelId } = useParams()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [message, setMessage] = useState('')
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: channel } = useQuery({
    queryKey: ['channel', channelId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/channels/${channelId}`)
      return response.data
    },
  })

  const { data: messages = [] } = useQuery({
    queryKey: ['messages', channelId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/messages/channels/${channelId}/messages`)
      return response.data
    },
    refetchInterval: 1000,
  })

  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      const response = await api.post(`/api/v1/messages/channels/${channelId}/messages`, { content })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages', channelId] })
      setMessage('')
    },
  })

  const addReactionMutation = useMutation({
    mutationFn: async ({ messageId, emoji }: { messageId: string; emoji: string }) => {
      const response = await api.post(`/api/v1/messages/messages/${messageId}/reactions`, { emoji })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages', channelId] })
    },
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      sendMessageMutation.mutate(message)
    }
  }

  const handleReaction = (messageId: string, emoji: string) => {
    addReactionMutation.mutate({ messageId, emoji })
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (!channel) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Channel Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center space-x-3">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            #{channel.name}
          </h2>
          {channel.description && (
            <span className="text-gray-600 dark:text-gray-400">
              {channel.description}
            </span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg: Message) => (
          <div key={msg.id} className="flex space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white font-medium text-sm">
                {msg.user.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <span className="font-medium text-gray-900 dark:text-white">
                  {msg.user.username}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {formatTime(msg.created_at)}
                </span>
              </div>
              <div className="text-gray-700 dark:text-gray-300 mb-2">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
              
              {/* Reactions */}
              {msg.reactions.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {msg.reactions.map((reaction) => (
                    <button
                      key={reaction.id}
                      onClick={() => handleReaction(msg.id, reaction.emoji)}
                      className={`px-2 py-1 rounded-full text-xs font-medium transition-colors ${
                        reaction.users.includes(user?.id || '')
                          ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {reaction.emoji} {reaction.count}
                    </button>
                  ))}
                </div>
              )}
              
              {/* Quick Reactions */}
              <div className="flex space-x-1">
                {['👍', '❤️', '😂', '😮', '😢', '😡'].map((emoji) => (
                  <button
                    key={emoji}
                    onClick={() => handleReaction(msg.id, emoji)}
                    className="text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded p-1 transition-colors"
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type a message..."
              className="input pr-10"
              disabled={sendMessageMutation.isPending}
            />
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
              <button
                type="button"
                onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              >
                <Smile className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              </button>
              <button
                type="button"
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              >
                <Paperclip className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={!message.trim() || sendMessageMutation.isPending}
            className="btn btn-primary px-4"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  )
}

export default Channel 