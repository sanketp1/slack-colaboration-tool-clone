import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

interface Channel {
  id: string
  name: string
  description?: string
  message_count: number
}

const Dashboard = () => {
  const { data: channels = [] } = useQuery<Channel[]>({
    queryKey: ['channels'],
    queryFn: async () => {
      const response = await api.get('/api/v1/channels/')
      return response.data
    },
  })

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome to Slack Clone
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Choose a channel to start chatting or join a video call
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {channels.map((channel) => (
            <div
              key={channel.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  #{channel.name}
                </h3>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {channel.message_count} messages
                </span>
              </div>
              
              {channel.description && (
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {channel.description}
                </p>
              )}
              
              <div className="flex space-x-2">
                <a
                  href={`/channel/${channel.id}`}
                  className="btn btn-primary flex-1 text-center"
                >
                  Join Chat
                </a>
                <a
                  href={`/call/${channel.id}`}
                  className="btn btn-secondary flex-1 text-center"
                >
                  Join Call
                </a>
              </div>
            </div>
          ))}
        </div>

        {channels.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 dark:text-gray-600 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No channels yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Create your first channel to get started
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard 