import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../lib/api'
import {
  LiveKitRoom,
  VideoConference,
  ControlBar,
  useTracks,
  Room,
  Track,
  Participant,
  RoomEvent,
  TrackPublication,
  RemoteTrackPublication,
  LocalTrackPublication,
} from '@livekit/components-react'
import { Mic, MicOff, Video, VideoOff, Phone, Share, Hand, Camera, CameraOff } from 'lucide-react'

// Utility function to handle AudioContext resumption
const resumeAudioContext = async () => {
  try {
    // Create a temporary audio context to resume it
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    if (audioContext.state === 'suspended') {
      await audioContext.resume()
    }
    await audioContext.close()
  } catch (error) {
    console.warn('Failed to resume AudioContext:', error)
  }
}

// Check browser compatibility
const checkBrowserCompatibility = () => {
  const issues: string[] = []
  
  if (!navigator.mediaDevices) {
    issues.push('Media devices not supported')
  }
  
  if (!navigator.mediaDevices?.getUserMedia) {
    issues.push('getUserMedia not supported')
  }
  
  if (!window.AudioContext && !(window as any).webkitAudioContext) {
    issues.push('AudioContext not supported')
  }
  
  return issues
}

const Call = () => {
  const { channelId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [token, setToken] = useState<string | null>(null)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [permissionsGranted, setPermissionsGranted] = useState(false)
  const [isRequestingPermissions, setIsRequestingPermissions] = useState(false)
  const [joinWithoutMedia, setJoinWithoutMedia] = useState(false)
  const [browserIssues, setBrowserIssues] = useState<string[]>([])

  const { data: channel } = useQuery({
    queryKey: ['channel', channelId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/channels/${channelId}`)
      return response.data
    },
  })

  useEffect(() => {
    // Check browser compatibility on component mount
    const issues = checkBrowserCompatibility()
    setBrowserIssues(issues)
  }, [])

  const requestMediaPermissions = async () => {
    setIsRequestingPermissions(true)
    try {
      // Resume AudioContext first
      await resumeAudioContext()
      
      // Request camera and microphone permissions
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      })
      
      // Stop the stream immediately after getting permissions
      stream.getTracks().forEach(track => track.stop())
      
      setPermissionsGranted(true)
      setError(null)
    } catch (err: any) {
      console.error('Media permission error:', err)
      if (err.name === 'NotAllowedError') {
        setError('Camera and microphone access is required to join the call. Please allow permissions and try again.')
      } else if (err.name === 'NotFoundError') {
        setError('No camera or microphone found. Please connect a device and try again.')
      } else if (err.name === 'NotSupportedError') {
        setError('Your browser does not support video calling. Please try a different browser.')
      } else {
        setError('Failed to access camera and microphone. Please check your device settings.')
      }
    } finally {
      setIsRequestingPermissions(false)
    }
  }

  const joinCallWithoutMedia = async () => {
    try {
      // Still try to resume AudioContext even without media
      await resumeAudioContext()
      setJoinWithoutMedia(true)
      setPermissionsGranted(true) // Skip permission check
    } catch (error) {
      console.warn('Failed to resume AudioContext:', error)
      // Continue anyway
      setJoinWithoutMedia(true)
      setPermissionsGranted(true)
    }
  }

  useEffect(() => {
    const getToken = async () => {
      if (!channelId || !user) return
      
      try {
        setIsConnecting(true)
        setError(null)
        const response = await api.post('/api/v1/video/token', {
          channel_id: channelId,
          user_id: user.id,
          username: user.username,
        })
        setToken(response.data.token)
      } catch (error) {
        console.error('Failed to get video token:', error)
        setError('Failed to join call. Please try again.')
      } finally {
        setIsConnecting(false)
      }
    }

    getToken()
  }, [channelId, user])

  const handleDisconnect = () => {
    navigate(`/channel/${channelId}`)
  }

  const handleConnectionError = (error: any) => {
    console.error('LiveKit connection error:', error)
    
    // Handle specific media errors
    if (error.message?.includes('Could not start video source') || 
        error.message?.includes('Could not start audio source')) {
      setError('Failed to access camera or microphone. Please check your device permissions and try again.')
    } else if (error.message?.includes('AudioContext was not allowed to start')) {
      setError('Audio access is required. Please allow microphone permissions and try again.')
    } else if (error.message?.includes('NotReadableError')) {
      setError('Camera or microphone is already in use by another application. Please close other apps and try again.')
    } else {
      setError('Connection failed. Please check your internet connection and try again.')
    }
  }

  // Show browser compatibility issues
  if (browserIssues.length > 0) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <div className="text-center max-w-md bg-gray-800 p-8 rounded-lg">
          <div className="mb-6">
            <Camera className="h-16 w-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Browser Not Supported</h2>
            <p className="text-gray-400 mb-4">
              Your browser doesn't support video calling features
            </p>
            <div className="text-left text-sm text-gray-300">
              <p className="font-semibold mb-2">Issues found:</p>
              <ul className="list-disc list-inside space-y-1">
                {browserIssues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="space-y-4">
            <button
              onClick={joinCallWithoutMedia}
              className="btn btn-secondary w-full"
            >
              <MicOff className="h-4 w-4 mr-2" />
              Try Without Media
            </button>
            
            <button
              onClick={() => navigate(`/channel/${channelId}`)}
              className="btn btn-secondary w-full"
            >
              Back to Channel
            </button>
          </div>
          
          <p className="text-xs text-gray-500 mt-4">
            Try using Chrome, Firefox, or Safari for the best experience
          </p>
        </div>
      </div>
    )
  }

  if (isConnecting) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Connecting to call...</p>
        </div>
      </div>
    )
  }

  if (isRequestingPermissions) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Requesting camera and microphone permissions...</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">Please allow access when prompted</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <div className="space-y-2">
            <button
              onClick={requestMediaPermissions}
              className="btn btn-primary w-full"
            >
              <Camera className="h-4 w-4 mr-2" />
              Grant Permissions
            </button>
            <button
              onClick={joinCallWithoutMedia}
              className="btn btn-secondary w-full"
            >
              <MicOff className="h-4 w-4 mr-2" />
              Join Without Media
            </button>
            <button
              onClick={() => navigate(`/channel/${channelId}`)}
              className="btn btn-secondary w-full"
            >
              Back to Channel
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!token) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400">Failed to join call</p>
          <button
            onClick={() => navigate(`/channel/${channelId}`)}
            className="btn btn-primary mt-4"
          >
            Back to Channel
          </button>
        </div>
      </div>
    )
  }

  // Show permission request if not granted yet
  if (!permissionsGranted) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <div className="text-center max-w-md bg-gray-800 p-8 rounded-lg">
          <div className="mb-6">
            <Camera className="h-16 w-16 text-primary-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Join Video Call</h2>
            <p className="text-gray-400">
              This call requires access to your camera and microphone
            </p>
          </div>
          
          <div className="space-y-4">
            <button
              onClick={requestMediaPermissions}
              className="btn btn-primary w-full"
            >
              <Camera className="h-4 w-4 mr-2" />
              Allow Camera & Microphone
            </button>
            
            <button
              onClick={joinCallWithoutMedia}
              className="btn btn-secondary w-full"
            >
              <MicOff className="h-4 w-4 mr-2" />
              Join Without Media
            </button>
            
            <button
              onClick={() => navigate(`/channel/${channelId}`)}
              className="btn btn-secondary w-full"
            >
              Cancel
            </button>
          </div>
          
          <p className="text-xs text-gray-500 mt-4">
            You can change these permissions later in your browser settings
          </p>
        </div>
      </div>
    )
  }

  const livekitUrl = import.meta.env.VITE_LIVEKIT_URL || 'ws://localhost:7880'

  return (
    <div className="h-full bg-gray-900">
      <LiveKitRoom
        token={token}
        serverUrl={livekitUrl}
        connect={true}
        video={!joinWithoutMedia}
        audio={!joinWithoutMedia}
        onDisconnected={handleDisconnect}
        onError={handleConnectionError}
      >
        <div className="h-full flex flex-col">
          {/* Call Header */}
          <div className="bg-gray-800 text-white px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <h2 className="text-xl font-semibold">
                #{channel?.name} - Video Call
              </h2>
              <span className="text-sm text-gray-400">
                {channel?.description}
              </span>
              {joinWithoutMedia && (
                <span className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">
                  Audio/Video Disabled
                </span>
              )}
            </div>
            <button
              onClick={handleDisconnect}
              className="btn bg-red-600 hover:bg-red-700 text-white"
            >
              <Phone className="h-4 w-4" />
              Leave Call
            </button>
          </div>

          {/* Video Conference */}
          <div className="flex-1">
            <VideoConference
              className="h-full"
            />
          </div>
        </div>
      </LiveKitRoom>
    </div>
  )
}

export default Call 