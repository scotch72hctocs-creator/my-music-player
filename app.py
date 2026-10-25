from flask import Flask, jsonify, render_template, request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import os

app = Flask(__name__, static_folder="static", static_url_path="/static")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()
    order = request.args.get("order", "relevance")
if order not in ("relevance", "viewCount", "date"):
    order = "relevance"
    if not query:
        return jsonify({"error": "検索キーワードを入力してください。"}), 400

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        app.logger.error("YOUTUBE_API_KEY が設定されていません")
        return jsonify({
            "error": "検索設定が未完了です。管理者にお問い合わせください。"
        }), 500

    params = {
        "key": api_key,
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": "JP",
        "order": order,
        "maxResults": 20,
    }
    url = "https://www.googleapis.com/youtube/v3/search?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "MyMusicPlayer/1.0"})

    try:
        with urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        videos = []
        seen_ids = set()
        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if not video_id or video_id in seen_ids:
                continue

            seen_ids.add(video_id)
            snippet = item.get("snippet", {})
            videos.append({
                "videoId": video_id,
                "title": snippet.get("title", ""),
                "author": snippet.get("channelTitle", ""),
                "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
            })

        return jsonify({"results": videos})

    except Exception:
        app.logger.exception("YouTube検索に失敗しました")
        return jsonify({
            "error": "検索に失敗しました。時間をおいて再度お試しください。"
        }), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
