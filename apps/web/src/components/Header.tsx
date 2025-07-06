import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { Moon, Sun, LogOut, User } from 'lucide-react'
import { useState } from 'react'

const Header = () => {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [showMenu, setShowMenu] = useState(false)

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            Slack Clone
          </h1>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5 text-gray-900 dark:text-white" />
            ) : (
              <Moon className="h-5 w-5 text-gray-900 dark:text-white" />
            )}
          </button>
          
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-gray-900 dark:text-white font-medium">
                {user?.username}
              </span>
            </button>
            
            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2">
                <button
                  onClick={logout}
                  className="w-full flex items-center space-x-2 px-4 py-2 text-left text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 