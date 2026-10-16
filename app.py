from flask import Flask, render_template, request, jsonify
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json

app = Flask(name)

@app.get("/")
def index():
return render_template("index.html")

@app.get("/api/search")
def search():
query = request.args.get("q", "").strip()

if not query:
    return jsonify({"error": "検索キーワードを入力してください。"}), 400

params = urlencode({
    "q": query,
    "type": "video",
    "region": "JP"
})

url = "https://invidious.f5.si/api/v1/search?" + params

req = Request(
    url,
    headers={"User-Agent": "MyMusicPlayer/1.0"}
)

try:
    with urlopen(req, timeout=15) as response:
        results = json.loads(response.read().decode("utf-8"))

    videos = []

    for item in results:
        if item.get("type") != "video" or not item.get("videoId"):
            continue

        videos.append({
            "videoId": item["videoId"],
            "title": item.get("title", ""),
            "author": item.get("author", ""),
            "videoUrl": "https://www.youtube.com/watch?v=" + item["videoId"],
            "thumbnail": (
                "https://i.ytimg.com/vi/"
                + item["videoId"]
                + "/mqdefault.jpg"
            )
        })

        if len(videos) >= 15:
            break

    return jsonify({"results": videos})

except Exception:
    app.logger.exception("YouTube検索に失敗しました")
    return jsonify({
        "error": "検索に失敗しました。時間をおいて再度お試しください。"
    }), 502

if name == "main":
app.run(host="127.0.0.1", port=5000, debug=False)
