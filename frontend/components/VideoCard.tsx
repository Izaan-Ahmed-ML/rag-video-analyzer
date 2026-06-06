type VideoData = {
  platform: string
  creator: string
  views: number
  likes: number
  comments: number
  engagement_rate: number
  upload_date: string
  hashtags: string[]
  followers_count?: number
  title?: string
}

type Props = {
  label: string
  data: VideoData | null
}

export default function VideoCard({ label, data }: Props) {
  if (!data) {
    return (
      <div className="border rounded-xl p-4 w-full min-h-48 flex items-center justify-center text-gray-400">
        Video {label} — paste a URL and click Analyze
      </div>
    )
  }

  return (
    <div className="border rounded-xl p-4 w-full space-y-2">
      <div className="flex items-center gap-2">
        <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
          Video {label}
        </span>
        <span className="text-xs text-gray-500 uppercase">{data.platform}</span>
      </div>

      {data.title && (
        <p className="font-semibold text-sm">{data.title}</p>
      )}

      <p className="text-sm">👤 {data.creator}</p>

      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <div className="bg-gray-100 rounded p-2">
          <p className="font-bold">{Number(data.views).toLocaleString()}</p>
          <p className="text-xs text-gray-500">Views</p>
        </div>
        <div className="bg-gray-100 rounded p-2">
          <p className="font-bold">{Number(data.likes).toLocaleString()}</p>
          <p className="text-xs text-gray-500">Likes</p>
        </div>
        <div className="bg-gray-100 rounded p-2">
          <p className="font-bold">{Number(data.comments).toLocaleString()}</p>
          <p className="text-xs text-gray-500">Comments</p>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded p-2 text-center">
        <p className="text-green-700 font-bold text-lg">
          {Number(data.engagement_rate).toFixed(2)}%
        </p>
        <p className="text-xs text-green-600">Engagement Rate</p>
      </div>

      {data.followers_count && (
        <p className="text-sm">👥 {Number(data.followers_count).toLocaleString()} followers</p>
      )}

      {data.hashtags && data.hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {data.hashtags.map((tag: string) => (
            <span key={tag} className="bg-blue-50 text-blue-600 text-xs px-2 py-1 rounded">
              #{tag}
            </span>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400">
        📅 {new Date(data.upload_date).toLocaleDateString()}
      </p>
    </div>
  )
}