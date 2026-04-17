"""
Local Blog Application (Flask)
A simple blogging platform that Selenium can automate reliably.
Runs on http://localhost:5000
"""
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)

# Simple file-based storage in data directory
POSTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "posts.json")

def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=2)

# ─── HTML Templates ───────────────────────────────────────────────

HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AutoBlog - AI Blog Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #e0e0e0; }
        .navbar { background: #1a1a2e; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #00d4ff; font-size: 24px; }
        .navbar a { color: #00d4ff; text-decoration: none; padding: 10px 20px; border: 1px solid #00d4ff; border-radius: 5px; }
        .navbar a:hover { background: #00d4ff; color: #0f0f0f; }
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        .post-card { background: #1a1a2e; border-radius: 10px; padding: 30px; margin-bottom: 20px; border-left: 4px solid #00d4ff; }
        .post-card h2 { color: #00d4ff; margin-bottom: 10px; }
        .post-card .meta { color: #888; font-size: 14px; margin-bottom: 15px; }
        .post-card p { line-height: 1.7; color: #ccc; }
        .empty { text-align: center; color: #666; padding: 60px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>AutoBlog</h1>
        <a href="/write" id="write-btn">Write a Post</a>
    </div>
    <div class="container">
        {% if posts %}
            {% for post in posts|reverse %}
            <div class="post-card">
                <h2>{{ post.title }}</h2>
                <div class="meta">Published on {{ post.date }}</div>
                <p>{{ post.content[:300] }}{% if post.content|length > 300 %}...{% endif %}</p>
            </div>
            {% endfor %}
        {% else %}
            <div class="empty">
                <h2>No posts yet</h2>
                <p>Click "Write a Post" to create your first blog post.</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

WRITE_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Write a Post - AutoBlog</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #e0e0e0; }
        .navbar { background: #1a1a2e; padding: 20px 40px; }
        .navbar h1 { color: #00d4ff; font-size: 24px; }
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        h2 { color: #00d4ff; margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #aaa; font-size: 14px; }
        input[type="text"] { width: 100%; padding: 12px; background: #1a1a2e; border: 1px solid #333; border-radius: 5px; color: #e0e0e0; font-size: 16px; margin-bottom: 20px; }
        textarea { width: 100%; height: 300px; padding: 12px; background: #1a1a2e; border: 1px solid #333; border-radius: 5px; color: #e0e0e0; font-size: 15px; line-height: 1.6; margin-bottom: 20px; resize: vertical; }
        input:focus, textarea:focus { outline: none; border-color: #00d4ff; }
        .btn-publish { background: #00d4ff; color: #0f0f0f; border: none; padding: 12px 30px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; }
        .btn-publish:hover { background: #00b8d9; }
        .success { background: #0d3d0d; border: 1px solid #1a8c1a; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #4caf50; }
    </style>
</head>
<body>
    <div class="navbar"><h1>AutoBlog</h1></div>
    <div class="container">
        <h2>Write a New Post</h2>
        {% if success %}
        <div class="success" id="success-msg">✅ Post published successfully!</div>
        {% endif %}
        <form method="POST" action="/publish" id="post-form">
            <label for="title">Title</label>
            <input type="text" id="title" name="title" placeholder="Enter your blog title..." required>
            <label for="content">Content</label>
            <textarea id="content" name="content" placeholder="Write your blog content here..." required></textarea>
            <button type="submit" class="btn-publish" id="publish-btn">Publish</button>
        </form>
    </div>
</body>
</html>
"""

# ─── Routes ───────────────────────────────────────────────────────

@app.route("/")
def home():
    posts = load_posts()
    return render_template_string(HOME_PAGE, posts=posts)

@app.route("/write")
def write():
    return render_template_string(WRITE_PAGE, success=False)

@app.route("/publish", methods=["POST"])
def publish():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if title and content:
        posts = load_posts()
        posts.append({
            "title": title,
            "content": content,
            "date": datetime.now().strftime("%B %d, %Y at %I:%M %p")
        })
        save_posts(posts)
        return render_template_string(WRITE_PAGE, success=True)
    return redirect(url_for("write"))

@app.route("/api/posts")
def api_posts():
    return jsonify(load_posts())

if __name__ == "__main__":
    print("Starting AutoBlog on http://localhost:5000")
    app.run(debug=True, port=5000)
