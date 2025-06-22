from flask import Flask, request, jsonify, send_from_directory
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__, static_folder='.')

POSTS_API = "https://api.rule34.xxx/index.php"
TAGS_API = "https://api.rule34.xxx/index.php"

def fetch_posts(tag="", page=0):
    # page is zero-based for API
    params = {
        "page": "dapi",
        "s": "post",
        "q": "index",
        "tags": tag,
        "pid": page
    }
    r = requests.get(POSTS_API, params=params)
    if r.status_code != 200:
        return {"error": "Failed to fetch posts"}

    root = ET.fromstring(r.content)
    posts = []
    for post in root.findall('post'):
        preview_url = post.attrib.get("preview_url")
        file_url = post.attrib.get("file_url")
        is_video = file_url.endswith((".webm", ".mp4"))
        posts.append({
            "preview": preview_url,
            "media": file_url,
            "type": "video" if is_video else "image",
            "tags": post.attrib.get("tags"),
            "id": post.attrib.get("id")
        })
    return {"posts": posts}

def fetch_tags(query=""):
    params = {
        "page": "dapi",
        "s": "tag",
        "q": "index",
        "name_pattern": query
    }
    r = requests.get(TAGS_API, params=params)
    if r.status_code != 200:
        return {"error": "Failed to fetch tags"}

    root = ET.fromstring(r.content)
    tags = []
    for tag in root.findall('tag'):
        tags.append({
            "name": tag.attrib.get("name"),
            "count": int(tag.attrib.get("count", "0")),
            "type": tag.attrib.get("type")
        })
    return {"tags": tags}

@app.route("/")
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route("/search")
def search():
    tag = request.args.get("tag", "")
    page = int(request.args.get("page", "1")) - 1  # zero-based for API
    return jsonify(fetch_posts(tag, page))

@app.route("/tags")
def tags():
    query = request.args.get("query", "")
    return jsonify(fetch_tags(query))

if __name__ == "__main__":
    app.run(debug=True)