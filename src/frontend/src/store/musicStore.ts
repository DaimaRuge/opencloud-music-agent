import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Song {
  id: string
  title: string
  artists: string[]
  album: string
  cover_url?: string
  duration: number
  preview_url?: string
  platform: string
}

interface MusicState {
  currentSong: Song | null
  isPlaying: boolean
  volume: number
  progress: number
  queue: Song[]
  searchResults: Song[]
  
  // Actions
  setCurrentSong: (song: Song) => void
  togglePlay: () => void
  setVolume: (volume: number) => void
  setProgress: (progress: number) => void
  addToQueue: (song: Song) => void
  nextSong: () => void
  previousSong: () => void
  setSearchResults: (songs: Song[]) => void
}

export const useMusicStore = create<MusicState>()(
  persist(
    (set, get) => ({
      currentSong: null,
      isPlaying: false,
      volume: 80,
      progress: 0,
      queue: [],
      searchResults: [],
      
      setCurrentSong: (song) => set({ currentSong: song, isPlaying: true }),
      togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
      setVolume: (volume) => set({ volume }),
      setProgress: (progress) => set({ progress }),
      addToQueue: (song) => set((state) => ({ queue: [...state.queue, song] })),
      setSearchResults: (songs) => set({ searchResults: songs }),
      nextSong: () => {
        const { queue } = get()
        if (queue.length > 0) {
          const [next, ...rest] = queue
          set({ currentSong: next, queue: rest, isPlaying: true, progress: 0 })
        }
      },
      previousSong: () => {
        // 历史记录功能待实现
      },
    }),
    {
      name: 'music-storage',
      partialize: (state) => ({ 
        volume: state.volume,
        currentSong: state.currentSong 
      })
    }
  )
)
