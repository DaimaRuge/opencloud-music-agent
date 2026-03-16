import React, { useState } from 'react'
import axios from 'axios'
import { useMusicStore } from '../store/musicStore'

const API_BASE = 'http://localhost:8000/api/v1'

export const SearchBar: React.FC = () => {
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(false)
  const { searchResults, setSearchResults, setCurrentSong } = useMusicStore()

  const handleSearch = async () => {
    if (!keyword.trim()) return
    
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/search`, {
        params: { q: keyword, limit: 20 }
      })
      setSearchResults(response.data.songs || [])
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch()
  }

  const playSong = (song: any) => {
    setCurrentSong(song)
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Search Input */}
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="搜索歌曲、歌手、专辑..."
          className="flex-1 px-4 py-3 bg-gray-800 rounded-lg border border-gray-700 focus:border-green-500 focus:outline-none text-white"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-6 py-3 bg-green-500 rounded-lg hover:bg-green-600 disabled:opacity-50 font-medium"
        >
          {loading ? '搜索中...' : '搜索'}
        </button>
      </div>

      {/* Results */}
      {searchResults.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-300 mb-4">
            搜索结果 ({searchResults.length})
          </h3>
          {searchResults.map((song, index) => (
            <div
              key={`${song.id}-${index}`}
              className="flex items-center gap-4 p-4 bg-gray-800 rounded-lg hover:bg-gray-750 transition-colors group"
            >
              <img
                src={song.cover_url || 'https://via.placeholder.com/60'}
                alt={song.title}
                className="w-16 h-16 rounded-lg object-cover"
              />
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-white truncate">{song.title}</h4>
                <p className="text-sm text-gray-400 truncate">
                  {song.artists?.join(', ')} · {song.album}
                </p>
                <span className="text-xs text-green-400 mt-1 inline-block">
                  {song.platform}
                </span>
              </div>
              <button
                onClick={() => playSong(song)}
                className="p-3 bg-green-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:scale-110"
              >
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M6.3 5.84a.5.5 0 01.77-.42l7.15 4.16a.5.5 0 010 .84l-7.15 4.16a.5.5 0 01-.77-.42V5.84z" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
