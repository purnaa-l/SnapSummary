import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the summarization prompt
prompt = ("You are a YouTube Summarizer. Focus on the overall message and tone of the video, "
          "avoiding any sensitive topics. Highlight key themes and important details while keeping "
          "the detailed summary clear and elaborate and concise.  "
          "The transcript text will be appended here: ")

# Function to extract transcript from YouTube video
def extract_transcript(youtube_url):
    try:
        video_id = youtube_url.split("v=")[1]  # Extract video ID from the URL
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine the transcript into a single string
        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript, video_id
    except TranscriptsDisabled:
        st.error("🚫 Subtitles are disabled for this video. Please choose a different video.")
        return None, None
    except Exception as e:
        st.error(f"⚠️ Error fetching transcript: {e}")
        return None, None

# Function to generate summary using Gemini with additional debugging
# Function to generate summary using Gemini with improved response handling
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")

    try:
        # Generate the content using the prompt and transcript text
        response = model.generate_content(prompt + transcript_text)

        # Debugging: Print out the response structure to verify access
        st.write("**API Raw Response:**", response)  # For debugging

        # Check if candidates exist in the response
        if response.candidates:
            for candidate in response.candidates:
                # Ensure that candidate has a 'content' attribute with 'parts'
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    # Extract the text from the first part if available
                    summary_text = candidate.content.parts[0].text
                    return summary_text
        
        # Error if no valid content is found
        st.error("🤖 No valid response content found. Please try a different video.")
        return None

    except Exception as e:
        # Handle unexpected exceptions
        st.error(f"⚠️ An error occurred during API processing: {e}")
        return None

# Streamlit app layout
st.title("🎬 YouTube Video Summarizer")
st.write("Quickly summarize YouTube videos using AI-generated content from transcripts.")

# Input for YouTube video URL
st.markdown("### 📥 Enter YouTube Video URL")
youtube_url = st.text_input("Paste the YouTube video link here...")

# Button to fetch transcript and generate summary
if st.button("✨ Generate Summary"):
    if youtube_url:
        with st.spinner("Fetching transcript and generating summary..."):
            # Fetch the transcript
            transcript_text, video_id = extract_transcript(youtube_url)
            if transcript_text:
                # Display the transcript for review (optional)
                st.write("**Transcript Extract:**")
                st.markdown(f"<div style='background-color: #f9f9f9; padding: 10px; border-radius: 5px;'>{transcript_text[:500]}...</div>", unsafe_allow_html=True)

                # Generate summary
                summary = generate_gemini_content(transcript_text, prompt)
                
                # Construct the thumbnail URL
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                st.image(thumbnail_url, caption="Video Thumbnail", use_column_width=True)  # Display thumbnail
                
                # Display summary
                if summary:
                    st.success("**🔍 Video Summary:**")
                    st.write(summary)
    else:
        st.warning("⚠️ Please enter a valid YouTube video URL.")

# Footer
st.markdown("---")
st.write("🛠️ **YouTube Video Summarizer Tool** | Powered by AI")
