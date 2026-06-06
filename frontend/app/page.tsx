"use client"
import { useState } from "react"
import VideoCard from "@/components/VideoCard"
import ChatPanel from "@/components/ChatPanel"

export default function Home() {
  const [ytUrl, setYtUrl] = useState("")
  const [igUrl, setIgUrl] = useState("")
  const [videoA, setVideoA] = useState(null)
  const [videoB, setVideoB] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    setLoading(true)
    try {
      const res = await fetch("http://localhost:8000/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_url: ytUrl, instagram_url: igUrl })
      })
      const data = await res.json()
      setVideoA(data.video_A)
      setVideoB(data.video_B)
    } catch (err) {
      console.error("Ingest failed:", err)
    }
    setLoading(false)
  }

  return (
    <main className="min-h-screen p-6 bg-gray-50">
      <h1 className="text-2xl font-bold mb-6 text-center">📊 RAG Video Analyzer</h1>

      <div className="flex flex-col md:flex-row gap-3 mb-6">
        <input
          className="border rounded-lg p-3 flex-1 text-sm"
          placeholder="YouTube URL"
          value={ytUrl}
          onChange={e => setYtUrl(e.target.value)}
        />
        <input
          className="border rounded-lg p-3 flex-1 text-sm"
          placeholder="Instagram Reel URL"
          value={igUrl}
          onChange={e => setIgUrl(e.target.value)}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg text-sm font-semibold disabled:opacity-50"
        >
              {loading ? (
      <span className="flex items-center gap-2">
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
        </svg>
        Analyzing...
      </span>
    ) : "Analyze"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <VideoCard label="A" data={videoA} />
        <VideoCard label="B" data={videoB} />
      </div>

      <ChatPanel />
    </main>
  )
}