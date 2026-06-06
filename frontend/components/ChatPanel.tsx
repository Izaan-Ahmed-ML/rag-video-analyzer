"use client"
import { useState, useRef, useEffect } from "react"

type Source = {
  video_id: string
  chunk_index: number
  platform: string
  creator: string
  preview: string
}

type Message = {
  role: "user" | "assistant"
  content: string
  sources?: Source[]
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || streaming) return

    const question = input
    setInput("")
    setStreaming(true)

    setMessages(prev => [...prev, { role: "user", content: question }])
    setMessages(prev => [...prev, { role: "assistant", content: "", sources: [] }])

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, session_id: "demo_session" })
      })

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        const lines = text.split("\n")

        for (const line of lines) {
          if (!line.startsWith("data:")) continue
          const raw = line.replace("data:", "").trim()
          if (raw === "[DONE]") { setStreaming(false); break }

          try {
            const parsed = JSON.parse(raw)

            if (parsed.token) {
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1].content += parsed.token
                return updated
              })
            }

            if (parsed.sources) {
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1].sources = parsed.sources
                return updated
              })
            }
          } catch {}
        }
      }
    } catch (err) {
      console.error("Chat error:", err)
    }

    setStreaming(false)
  }

  return (
    <div className="border rounded-xl flex flex-col h-[500px]">
      <div className="p-3 border-b font-semibold text-sm">
        💬 Ask about the videos
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-8">
            Ask anything about Video A or Video B
          </p>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-xl px-4 py-2 text-sm ${
              msg.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
            }`}>
              <p className="whitespace-pre-wrap">
                {msg.content || (streaming && i === messages.length - 1 
                    ? <span className="animate-pulse text-gray-400">Thinking...</span>
                    : ""
                )}
                </p>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 space-y-1">
                  {msg.sources.map((s, j) => (
                    <div key={j} className="text-xs bg-white border rounded px-2 py-1 text-gray-500">
                      📎 Video {s.video_id} · Chunk {s.chunk_index} · {s.creator}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {streaming && (
            <div className="flex justify-start">
                <div className="bg-gray-100 rounded-xl px-4 py-2 text-sm text-gray-400 animate-pulse">
                ● ● ●
                </div>
            </div>
            )}
        <div ref={bottomRef} />
      </div>

      <div className="p-3 border-t flex gap-2">
        <input
          className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ask about the videos..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          disabled={streaming}
        />
        <button
          onClick={sendMessage}
          disabled={streaming}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-50"
        >
          {streaming ? "..." : "Send"}
        </button>
      </div>
    </div>
  )
}