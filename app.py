from flask import Flask, render_template, request, jsonify
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import os

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "検索キーワードを入力してください。"}), 400

    api_key = os.environ.get("YOUTUBE_API_KEY")

    if not api_key:
        app.logger.error("YOUTUBE_API_KEY が設定されていません")
        return jsonify({
            "error": "検索設定が未完了です。管理者にお問い合わせください。"
        }), 500

    videos = []
    seen_ids = set()
    max_videos = 50
    max_pages = 5

    try:
        for page in range(max_pages):
            params = {
                "key": api_key,
                "part": "snippet",
                "q": query,
                "type": "video",
                "regionCode": "JP",
                "maxResults": min(50, max_videos - len(videos)),
                "pageToken": None,
            }

            if page > 0:
                params["pageToken"] = next_page_token
            else:
                params.pop("pageToken")

            url = "https://www.googleapis.com/youtube/v3/search"

            req = Request(
                url + "?" + urlencode(params),
                headers={"User-Agent": "MyMusicPlayer/1.0"}
            )

            with urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                video_id = item.get("id", {}).get("videoId")
                if not video_id or video_id in seen_ids:
                    continue

                seen_ids.add(video_id)
                snippet = item.get("snippet", {})

                videos.append({
                    "videoId": video_id,
                    "title": snippet.get("title", ""),
                    "author": snippet.get("channelTitle", ""),
                    "videoUrl": "https://www.youtube.com/watch?v=" + video_id,
                    "thumbnail": "https://i.ytimg.com/vi/" + video_id + "/mqdefault.jpg"
                })

                if len(videos) >= max_videos:
                    break

            if len(videos) >= max_videos:
                break

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        return jsonify({"results": videos})

    except Exception:
        app.logger.exception("YouTube検索に失敗しました")
        return jsonify({
            "error": "検索に失敗しました。時間をおいて再度お試しください。"
        }), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
