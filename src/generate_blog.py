"""
Generate Blog Content using Google Gemini API.
Saves the generated title and content to text files for the Selenium publisher to pick up.
Supports --direct-publish flag for automated mode (Jenkins).
"""
import os
import argparse
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def suggest_topic():
    """Use Gemini to brainstorm a trending technical topic."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Set it in .env file.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = "Suggest one trending technical blog topic relevant to software engineering, AI, or web development. Return ONLY the topic name, no extra text."
    
    print("[Discovery] Scouting for a trending topic...")
    response = model.generate_content(prompt)
    topic = response.text.strip()
    print(f"[Discovery] AI suggested topic: '{topic}'")
    return topic

def generate_blog(topic):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Set it in .env file.")

    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1500,
    }

    system_instruction = """You are a world-class technical blog writer. 
Write engaging, professional articles with clear structure.
Structure: Title on first line, then a hook paragraph, 2-3 H2 sections, and a conclusion.
Tone: Authoritative, insightful, accessible."""

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction
    )

    prompt = f"Write a thought-leadership blog post about: {topic}. Title on the first line, then content."

    print(f"Generating blog post about '{topic}'...")
    response = model.generate_content(prompt)

    # Split title and content
    parts = response.text.strip().split('\n', 1)
    title = parts[0].replace("# ", "").replace("**", "").strip()
    content = parts[1].strip() if len(parts) > 1 else response.text

    return title, content

def main():
    parser = argparse.ArgumentParser(description="Generate a blog post using Gemini AI.")
    parser.add_argument("--topic", type=str, default="The Future of AI in Software Testing",
                        help="Topic for the blog post")
    parser.add_argument("--random-topic", action="store_true",
                        help="Ask AI to suggest a trending topic automatically")
    parser.add_argument("--direct-publish", action="store_true",
                        help="Skip preview - save as ready for auto-publishing")
    args = parser.parse_args()

    topic = args.topic
    if args.random_topic:
        topic = suggest_topic()

    title, content = generate_blog(topic)

    # Save to text files in the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    with open(os.path.join(data_dir, "blog_title.txt"), "w", encoding="utf-8") as f:
        f.write(title)
    with open(os.path.join(data_dir, "blog_content.txt"), "w", encoding="utf-8") as f:
        f.write(content)

    print("\n--- Generation Complete ---")
    print(f"Title: {title}")
    print(f"Content length: {len(content)} chars")
    print(f"Mode: {'DIRECT PUBLISH' if args.direct_publish else 'PREVIEW (manual approval needed)'}")
    print("Files saved: blog_title.txt, blog_content.txt")

if __name__ == "__main__":
    main()
