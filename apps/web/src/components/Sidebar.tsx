import { Link, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Hash, Video, X } from 'lucide-react'
import { useState } from 'react'
import { api } from '../lib/api'

interface Channel {
  id: string
  name: string
  description?: string
}

interface CreateChannelData {
  name: string
  description?: string
}

const Sidebar = () => {
  const { channelId } = useParams()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [channelName, setChannelName] = useState('')
  const [channelDescription, setChannelDescription] = useState('')
  const queryClient = useQueryClient()

  const { data: channels = [] } = useQuery<Channel[]>({
    queryKey: ['channels'],
    queryFn: async () => {
      const response = await api.get('/api/v1/channels/')
      return response.data
    },
  })

  const createChannelMutation = useMutation({
    mutationFn: async (data: CreateChannelData) => {
      const response = await api.post('/api/v1/channels/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['channels'] })
      setShowCreateModal(false)
      setChannelName('')
      setChannelDescription('')
    },
  })

  const handleCreateChannel = (e: React.FormEvent) => {
    e.preventDefault()
    if (channelName.trim()) {
      createChannelMutation.mutate({
        name: channelName.trim(),
        description: channelDescription.trim() || undefined,
      })
    }
  }

  return (
    <>
      <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Channels
            </h2>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <Plus className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <nav className="p-2">
            {channels.map((channel) => (
              <div key={channel.id} className="space-y-1">
                <Link
                  to={`/channel/${channel.id}`}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    channelId === channel.id
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Hash className="h-4 w-4" />
                  <span>{channel.name}</span>
                </Link>
                
                <Link
                  to={`/call/${channel.id}`}
                  className="flex items-center space-x-2 px-3 py-1 ml-6 rounded text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <Video className="h-3 w-3" />
                  <span>Join Call</span>
                </Link>
              </div>
            ))}
          </nav>
        </div>
      </div>

      {/* Create Channel Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Create New Channel
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <X className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
            
            <form onSubmit={handleCreateChannel}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Channel Name
                </label>
                <input
                  type="text"
                  value={channelName}
                  onChange={(e) => setChannelName(e.target.value)}
                  placeholder="e.g., general"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={channelDescription}
                  onChange={(e) => setChannelDescription(e.target.value)}
                  placeholder="What is this channel about?"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!channelName.trim() || createChannelMutation.isPending}
                  className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {createChannelMutation.isPending ? 'Creating...' : 'Create Channel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}

export default Sidebar 