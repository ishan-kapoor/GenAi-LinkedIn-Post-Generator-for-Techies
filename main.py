import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post


# Options for length and language
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]


# Main app layout
def main():
    st.subheader("📝GenAi LinkedIn Post Generator for Techies: By Ishan Kapoor")
    st.write("This tool is built using Streamlit, Meta's llama-3.2, Langchain, Groq and Few-Shot Learning to generate LinkedIn posts for Techeis. For more such tools and projects, visit [https://ishankapoor.netlify.app/]")
    st.write("Select the topic, length, and language of the post. Click on the 'Generate' button to generate a post.")

    # Create three columns for the dropdowns
    col1, col2, col3 = st.columns(3)

    fs = FewShotPosts()
    tags = fs.get_tags()
    with col1:
        # Dropdown for Topic (Tags)
        selected_tag = st.selectbox("Topic", options=tags)

    with col2:
        # Dropdown for Length
        selected_length = st.selectbox("Length", options=length_options)

    with col3:
        # Dropdown for Language
        selected_language = st.selectbox("Language", options=language_options)



    # Generate Button
    if st.button("Generate"):
        post = generate_post(selected_length, selected_language, selected_tag)
        st.write(post)


# Run the app
if __name__ == "__main__":
    main()
