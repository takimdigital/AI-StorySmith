import streamlit as st
import os
from book_generator.file_utils import sanitize_filename
from book_generator.state_manager import save_state, load_state
from book_generator.api_client import ApiClient
from book_generator.content_generator import ContentGenerator
from book_generator.book_compiler import BookCompiler

# --- Helper Functions ---
def initialize_clients():
    """Initializes and returns the API and content generator clients."""
    api_client = ApiClient()
    content_generator = ContentGenerator(api_client, st.session_state.base_dir)
    return content_generator

# --- Page 1: Welcome Page ---
def welcome_page():
    st.title("📖 Welcome to the Author's Assistant!")
    st.write("Let's bring your story to life.")
    col1, col2 = st.columns(2)
    if col1.button("Start a New Book", use_container_width=True):
        st.session_state.clear()
        st.session_state.page = 'setup'
        st.rerun()
    if col2.button("Load an Existing Project", use_container_width=True):
        projects = [d for d in os.listdir('generated_content') if os.path.isdir(os.path.join('generated_content', d))]
        if projects:
            project_to_load = st.selectbox("Select a project to load", projects)
            if st.button("Load Project"):
                base_dir = os.path.join('generated_content', project_to_load)
                state = load_state(base_dir)
                if state:
                    for k, v in state.items():
                        st.session_state[k] = v
                    st.session_state.page = 'writing_studio'
                    st.rerun()
                else:
                    st.error("Could not load project state.")
        else:
            st.info("No projects found.")

# --- Page 2: Project Setup Page ---
def setup_page():
    st.title("Project Setup Desk")
    st.write("First, let's establish the core of your story.")
    with st.form("foundation_form"):
        book_title = st.text_input("Book Title", value=st.session_state.get('book_title', ''))
        story_idea = st.text_area("What is your groundbreaking story idea?", height=150, value=st.session_state.get('story_idea', ''))
        tone = st.text_input("What is the desired tone?", value=st.session_state.get('tone', ''))
        num_chapters = st.number_input("How many chapters?", min_value=1, max_value=100, value=st.session_state.get('num_chapters', 5))

        if st.form_submit_button("Lay the Foundation"):
            if not all([book_title, story_idea, tone]):
                st.error("Please fill out all fields!")
            else:
                st.session_state.book_title = book_title
                st.session_state.sanitized_title = sanitize_filename(book_title)
                st.session_state.base_dir = os.path.join('generated_content', st.session_state.sanitized_title)
                st.session_state.story_idea = story_idea
                st.session_state.tone = tone
                st.session_state.num_chapters = num_chapters
                os.makedirs(st.session_state.base_dir, exist_ok=True)
                st.session_state.page = 'writing_studio'
                st.session_state.writing_step = 'premise'
                st.rerun()

# --- Page 3: Interactive Writing Studio ---
def writing_studio_page():
    st.title("The Interactive Writing Studio")
    content_generator = initialize_clients()

    steps = ["Premise", "Title", "Outline", "Chapters", "Publish"]
    current_step_index = steps.index(st.session_state.get('writing_step', 'premise'))
    st.markdown(f"**Step {current_step_index + 1} of {len(steps)}: {steps[current_step_index]}**")
    st.progress((current_step_index + 1) / len(steps))

    if st.session_state.writing_step == 'premise':
        st.header("1. Generate the Premise")
        if st.button("Generate Premise"):
            with st.spinner("Crafting a compelling premise..."):
                st.session_state.premise = content_generator.generate_premise(st.session_state.story_idea, st.session_state.tone)

        if 'premise' in st.session_state:
            st.session_state.premise = st.text_area("Premise", value=st.session_state.premise, height=200)
            col1, col2 = st.columns([1, 1])
            if col1.button("Regenerate", use_container_width=True):
                 with st.spinner("Rethinking the premise..."):
                    st.session_state.premise = content_generator.generate_premise(st.session_state.story_idea, st.session_state.tone)
            if col2.button("Approve & Continue →", type="primary", use_container_width=True):
                st.session_state.writing_step = 'title'
                st.rerun()

    elif st.session_state.writing_step == 'title':
        st.header("2. Generate the Title")
        st.info(f"**Premise:** {st.session_state.premise}")
        if st.button("Generate Title"):
            with st.spinner("Searching for the perfect title..."):
                st.session_state.title = content_generator.generate_title(st.session_state.premise, st.session_state.story_idea, st.session_state.tone)

        if 'title' in st.session_state:
            st.session_state.title = st.text_area("Title", value=st.session_state.title, height=50)
            col1, col2 = st.columns([1, 1])
            if col1.button("Regenerate", use_container_width=True):
                with st.spinner("Finding another title..."):
                    st.session_state.title = content_generator.generate_title(st.session_state.premise, st.session_state.story_idea, st.session_state.tone)
            if col2.button("Approve & Continue →", type="primary", use_container_width=True):
                st.session_state.writing_step = 'outline'
                st.rerun()

    elif st.session_state.writing_step == 'outline':
        st.header("3. Generate the Narrative Outline")
        st.info(f"**Title:** {st.session_state.title}")
        if st.button("Generate Full Outline"):
            with st.spinner("Building the story's backbone... This may take a moment."):
                toc = content_generator.generate_toc(st.session_state.premise, st.session_state.story_idea, st.session_state.tone, st.session_state.num_chapters)
                st.session_state.toc = toc
                content_types = content_generator.identify_content_types(toc, st.session_state.story_idea, st.session_state.premise, st.session_state.tone)
                refined_types = content_generator.refine_content_types(content_types, st.session_state.premise, st.session_state.tone)
                deepened_narrative = content_generator.deepen_narrative(refined_types, st.session_state.premise, st.session_state.tone)
                st.session_state.deepened_narrative = deepened_narrative

        if 'deepened_narrative' in st.session_state:
            st.session_state.deepened_narrative = st.text_area("Narrative Outline", value=st.session_state.deepened_narrative, height=400)
            col1, col2 = st.columns([1, 1])
            if col1.button("Regenerate", use_container_width=True):
                 with st.spinner("Restructuring the narrative..."):
                    toc = content_generator.generate_toc(st.session_state.premise, st.session_state.story_idea, st.session_state.tone, st.session_state.num_chapters)
                    st.session_state.toc = toc
                    content_types = content_generator.identify_content_types(toc, st.session_state.story_idea, st.session_state.premise, st.session_state.tone)
                    refined_types = content_generator.refine_content_types(content_types, st.session_state.premise, st.session_state.tone)
                    st.session_state.deepened_narrative = content_generator.deepen_narrative(refined_types, st.session_state.premise, st.session_state.tone)
            if col2.button("Approve & Continue →", type="primary", use_container_width=True):
                st.session_state.writing_step = 'chapters'
                st.rerun()

    elif st.session_state.writing_step == 'chapters':
        st.header("4. Write the Chapters")
        st.markdown(st.session_state.toc)
        if 'chapters' not in st.session_state:
            st.session_state.chapters = {}

        if st.button("Write All Chapters", type="primary"):
            progress_bar = st.progress(0, "Starting chapter generation...")
            chapters_list = []

            with st.spinner("Generating chapter outlines..."):
                content_generator.extract_chapters_regex()
                content_generator.generate_first_outline(st.session_state.premise, st.session_state.num_chapters)
                content_generator.generate_remaining_outlines(st.session_state.num_chapters)

            for i in range(st.session_state.num_chapters):
                chapter_num = i + 1
                with st.spinner(f"Writing Chapter {chapter_num}..."):
                    if chapter_num == 1:
                        chapter_text = content_generator.generate_first_chapter(st.session_state.tone)
                    else:
                        chapter_text = content_generator.generate_remaining_chapters(chapter_num, st.session_state.tone)[-1]
                    chapters_list.append(chapter_text)
                    st.session_state.chapters[f"Chapter {chapter_num}"] = chapter_text
                progress_bar.progress((chapter_num) / st.session_state.num_chapters, f"Chapter {chapter_num} complete!")
            st.session_state.all_chapters_list = chapters_list
            progress_bar.progress(1.0, "All chapters are complete!")

        for chapter_title, chapter_text in st.session_state.chapters.items():
            with st.expander(f"**{chapter_title}**"):
                st.write(chapter_text)
        if len(st.session_state.chapters) == st.session_state.num_chapters:
            if st.button("Continue to Publishing →", type="primary"):
                st.session_state.writing_step = 'publish'
                st.rerun()

    elif st.session_state.writing_step == 'publish':
        publish_page()
# ... (Publishing page and Main App Router remain the same) ...
def publish_page():
    st.title("The Publishing House")
    st.header("Your Masterpiece is Ready!")

    compiler = BookCompiler(st.session_state.base_dir, st.session_state.title, st.session_state.toc, st.session_state.all_chapters_list)

    with st.expander("Read Your Full Manuscript"):
        full_text = compiler._get_full_content_txt()
        st.text_area("Full Manuscript", value=full_text, height=500, disabled=True)

    st.header("Download Your Masterpiece")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="Download as .txt",
            data=compiler._get_full_content_txt().encode('utf-8'),
            file_name=f"{st.session_state.sanitized_title}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.download_button(
            label="Download as .md",
            data=compiler._get_full_content_md().encode('utf-8'),
            file_name=f"{st.session_state.sanitized_title}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col3:
        pdf_path = os.path.join(st.session_state.base_dir, f"{st.session_state.sanitized_title}.pdf")
        compiler.save_as_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download as .pdf",
                data=f,
                file_name=f"{st.session_state.sanitized_title}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'

    if st.session_state.page != 'welcome':
        with st.sidebar:
            st.header("Project Control Center")
            st.text_input("Book Title", value=st.session_state.get('book_title', ''), disabled=True)
            if 'base_dir' in st.session_state:
                st.write(f"**Project Folder:** `{st.session_state.base_dir}`")
            st.radio("Interaction Mode", ["Manual", "Auto"], index=0, disabled=True)

            if st.button("Save Progress", use_container_width=True):
                if 'base_dir' in st.session_state:
                    state_to_save = {k: v for k, v in st.session_state.items()}
                    save_state(st.session_state.base_dir, state_to_save)
                    st.success("Project saved successfully!")
                else:
                    st.error("Cannot save. Please start a project first.")

    if st.session_state.page == 'welcome':
        welcome_page()
    elif st.session_state.page == 'setup':
        setup_page()
    elif st.session_state.page == 'writing_studio':
        writing_studio_page()

if __name__ == "__main__":
    main()
