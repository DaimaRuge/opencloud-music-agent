import React, { useState, useEffect } from 'react'
import { MusicPlayer } from './components/MusicPlayer'
import { SearchBar } from './components/SearchBar'
import { useMusicStore } from './store/musicStore'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('search')
  const { currentSong } = useMusicStore()

  return (
    <div className="min-h-screen bg-gray-900 text-white pb-24">
      {/* Header */}
      <header className="bg-gray-800 p-4 shadow-lg">
        <h1 className="text-2xl font-bold text-green-400">🎵 OpenCloud Music</h1>
        <p className="text-sm text-gray-400">跨平台音乐聚合 AI Agent</p>
      </header>

      {/* Navigation */}
      <nav className="flex space-x-4 p-4 bg-gray-800 border-b border-gray-700">
        {['search', 'library', 'recommendations', 'statistics'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg capitalize ${
              activeTab === tab ? 'bg-green-500 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {activeTab === 'search' && (
          <div>
            <SearchBar />
          </div>
        )}
        {activeTab === 'library' && (
          <div className="text-center text-gray-500 mt-20">
            <p>我的音乐库</p>
            <p className="text-sm mt-2">功能开发中...</p>
          </div>
        )}
        {activeTab === 'recommendations' && (
          <div className="text-center text-gray-500 mt-20">
            <p>每日推荐</p>
            <p className="text-sm mt-2">功能开发中...</p>
          </div>
        )}
        {activeTab === 'statistics' && (
          <div className="text-center text-gray-500 mt-20">
            <p>听歌统计</p>
            <p className="text-sm mt-2">功能开发中...</p>
          </div>
        )}
      </main>

      {/* Music Player */}
      {currentSong && <MusicPlayer />}
    </div>
  )
}

export default App
