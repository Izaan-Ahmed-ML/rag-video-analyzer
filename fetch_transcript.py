import os
from urllib import response
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
import sys

# #Ensure that the output is encoded in UTF-8(example cp1252)
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
VIDEO_ID = "G11ekgY6wYY"

import json

def get_Youtube_video_info(api_key, video_id):
    if not api_key:
        return None
    youtube = build("youtube", "v3", developerKey=api_key)

    request = youtube.videos().list(
        part="snippet,statistics,contentDetails,status",
        id=video_id
    )
    

    response = request.execute()
	
    # Pretty-print the full JSON response
    # print(json.dumps(response, indent=4, ensure_ascii=False))
    likes = int(response["items"][0]["statistics"].get("likeCount", 0))
    views = int(response["items"][0]["statistics"].get("viewCount", 0))
    comments = int(response["items"][0]["statistics"].get("commentCount", 0))
    engagement_rate = (likes+comments) / views * 100 if views > 0 else None
	
    return {
        "platform": "youtube",
        "video_id": video_id,
        "creator": response["items"][0]["snippet"]["channelTitle"],
        "title": response["items"][0]["snippet"]["title"],
        "published_at": response["items"][0]["snippet"]["publishedAt"],
        "views": response["items"][0]["statistics"]["viewCount"],
        "likes": response["items"][0]["statistics"]["likeCount"],
        "comments": response["items"][0]["statistics"]["commentCount"],
        "engagement_rate": engagement_rate
    }
def youtube_transcript(video_id: str) -> str:
	
	ytt_api = YouTubeTranscriptApi()
	YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
	VIDEO_ID = "G11ekgY6wYY"

	transcript = ytt_api.fetch(VIDEO_ID)
	result = " ".join(snippet.text for snippet in transcript)
	return result



# Fetch Instagram post metadata (likes, comments, video_view_count, owner_username,
# owner_profile.followers, caption, date, is_video) in a clean JSON format.

import re
import json
from instaloader import Instaloader, Post

import os

os.environ["PATH"] += r";C:\Users\busin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"

import shutil

print(shutil.which("ffmpeg"))


def extract_shortcode(url: str) -> str:
		url = url.strip().strip('"').strip("'")
		m = re.search(r"/p/([A-Za-z0-9_-]+)/?", url)
		if m:
			return m.group(1)
		raise ValueError("Could not extract shortcode from URL")
		L = Instaloader(
		download_comments=False,
		save_metadata=False,
		download_geotags=False
	)
		


#Instagaram Transcript fetching code
def instagram_transcript(url: str) -> str:
	L = Instaloader(
	download_comments=False,
	save_metadata=False,
	download_geotags=False
)


	shortcode = extract_shortcode(url)

	post = Post.from_shortcode(L.context, shortcode)

	# Download the reel/video
	L.download_post(post, target="instagram_reels")

	print("Downloaded successfully")

	folder = "instagram_reels"

	video_file = None

	for file in os.listdir(folder):
		if file.endswith(".mp4"):
			video_file = os.path.join(folder, file)
			break

	print(video_file)
	#Transcribe the video using Whisper
	import whisper

	model = whisper.load_model("base")

	result = model.transcribe(video_file)

	transcript = result["text"]
	return transcript

	

def get_instagaram_video_info(url: str) -> dict:

	def fetch_instagram_post_data(url: str) -> dict:
		L = Instaloader()
		shortcode = extract_shortcode(url)
		post = Post.from_shortcode(L.context, shortcode)

		owner_profile = getattr(post, 'owner_profile', None)
		followers = None
		if owner_profile is not None:
			try:
				followers = owner_profile.followers
			except Exception:
				followers = None

		data = {
			'shortcode': shortcode,
			'likes': getattr(post, 'likes', None),
			'comments': getattr(post, 'comments', None),
			'video_view_count': getattr(post, 'video_view_count', None),
			'owner_username': getattr(post, 'owner_username', None),
			'owner_followers': followers,
			'caption': getattr(post, 'caption', None),
			'date_utc': getattr(post, 'date_utc', None).isoformat() if getattr(post, 'date_utc', None) else None,
			'is_video': getattr(post, 'is_video', None),
			'transcript': getattr(post, 'caption', None) if getattr(post, 'is_video', None) else None
		}
		return data

	if __name__ == '__main__':
		try:
			result = fetch_instagram_post_data(public_url)
			print(json.dumps(result, ensure_ascii=False, indent=2))
		except Exception as e:
			print(json.dumps({'error': str(e)}))

	insta_likes = fetch_instagram_post_data(public_url)["likes"]
	insta_comments = fetch_instagram_post_data(public_url)["comments"]
	insta_views = fetch_instagram_post_data(public_url)["video_view_count"]

	engagement = ((int(insta_likes or 0) + int(insta_comments or 0)) / int(insta_views or 1) * 100) if insta_views else None
	# print(f"Likes: {insta_likes}, Comments: {insta_comments}, Views: {insta_views}")
	# # try:
	# # 	if insta_views is None or insta_views == 0:
	# # 		raise ValueError("Video view count unavailable because this is not a video post or view count is zero.")
	# # 	engagement = (int(insta_likes or 0) + int(insta_comments or 0)) / int(insta_views) * 100
	# # 	print(f"Engagement rate: {engagement:.2f}%")
	# # except Exception as exc:
	# # 	print(f"Could not calculate engagement rate: {exc}")

	return {
		"platform": "instagram",
		"likes": insta_likes,
		"comments": insta_comments,
		"views": insta_views,
		"followers_count": fetch_instagram_post_data(public_url)["owner_followers"],
		"hashtags": re.findall(r"#(\w+)", fetch_instagram_post_data(public_url)["caption"] or ""),
		"upload_date": fetch_instagram_post_data(public_url)["date_utc"],
		"duration": None,
		"engagement_rate": engagement,
		"creator": fetch_instagram_post_data(public_url)["owner_username"],
		
	}
    
public_url = "https://www.instagram.com/p/DVRZKJmDsIl/"
metadata_instagaram = get_instagaram_video_info(public_url)
Transcript_instagaram=instagram_transcript(public_url)
print(metadata_instagaram,Transcript_instagaram)

#ingesting vector store with chromadb and BAAI/bge-base-en-v1.5 Hugging Face model for embeddings
import os

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")

import chromadb
from langchain_chroma import Chroma
# setting up embeddings with a publicly available Hugging Face model
from langchain_huggingface import HuggingFaceEmbeddings

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)

def ingest_to_vector_store(transcript: str, metadata: dict, label: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_text(transcript)

    # Build one metadata summary chunk — goes in as searchable text
    metadata_chunk = f"""Video {label} Metadata:
Platform: {metadata.get('platform')}
Creator: {metadata.get('creator')}
Views: {metadata.get('views')}
Likes: {metadata.get('likes')}
Comments: {metadata.get('comments')}
Engagement Rate: {metadata.get('engagement_rate')}%
Follower Count: {metadata.get('followers_count', 'N/A')}
Hashtags: {metadata.get('hashtags', [])}
Upload Date: {metadata.get('published_at') or metadata.get('upload_date')}"""

    all_chunks = [metadata_chunk] + chunks

    docs_metadata = [
        {
            "video_id": label,
            "platform": metadata.get("platform"),
            "creator": metadata.get("creator"),
            "engagement_rate": metadata.get("engagement_rate"),
            "followers_count": metadata.get("followers_count"),
            "hashtags": str(metadata.get("hashtags")),
            "chunk_index": i,
        }
        for i, _ in enumerate(all_chunks)
    ]

    vectorstore = Chroma(
        collection_name="videos",
        embedding_function=embeddings,
        client=chroma_client,
    )
    vectorstore.add_texts(texts=all_chunks, metadatas=docs_metadata)
    return vectorstore

metadata_youtube = get_Youtube_video_info(
    YOUTUBE_API_KEY,
    VIDEO_ID
)
print(metadata_youtube)
vectorstore = ingest_to_vector_store(
    transcript=youtube_transcript(VIDEO_ID),
    metadata=metadata_youtube,
    label="A"
)

vectorstore = ingest_to_vector_store(
    transcript=Transcript_instagaram,
    metadata=metadata_instagaram,
    label="B"
)

print("Ingestion complete.")

results = vectorstore.similarity_search(
    "solution for getting transcript of a video in seconds",
    k=3
)

for doc in results:
    print("\nTEXT:")
    print(doc.page_content)

    print("\nMETADATA:")
    print(doc.metadata)





    

