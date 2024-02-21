import re
import os
from openai import OpenAI  

class StoryGenerator:
    def __init__(self, base_url="http://localhost:1234/v1", api_key="not-needed", temperature=0.7):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.temperature = temperature
        # Initialize base_dir later when book_title is known
        self.base_dir = None

    def setup_project(self):
        book_title = input("First things first, what's the title of your Folder name masterpiece? ")
        self.base_dir = os.path.join('generated_content', self.sanitize_filename(book_title))
        os.makedirs(self.base_dir, exist_ok=True)
        self.main()

    def sanitize_filename(self, filename):
        """
        Sanitizes filenames to remove or replace invalid characters.
        """
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def call_openai_api(self, messages, model="local-model"):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.temperature,
            )
            content = response.choices[0].message.content
            return content
        except Exception as e:
            print(f"Error calling API: {str(e)}")
            return None

    def save_to_file(self, filename, content):
        # This method saves 'content' to a file named 'filename' in the specified base directory
        filepath = os.path.join(self.base_dir, filename)  # Use self.base_dir to construct the filepath
        with open(filepath, "w", encoding='utf-8') as file:
            file.write(content)


    def load_from_file(self, filename):
        filepath = os.path.join(self.base_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None

    def generate_content(self, prompt, filename):
        content = self.load_from_file(filename)
        if content is None:  # If content doesn't exist, proceed to generate
            content = self.call_openai_api(prompt)
            self.save_to_file(filename, content)
        return content

    def generate_premise(self, story_idea, tone):
        premise_prompt = [
            {
                "role": "system",
                "content": "Create a compelling premise for a story. The premise should include (1) a protagonist described with an adjective and a noun, (2) their primary goal, (3) the central situation or crisis they face, and (4) a unique element or 'special sauce' that sets the story apart. This unique element could be a fresh perspective, a distinctive character voice, or an intriguing take on current events. Ensure the premise is concise yet captures the essence of the story idea and tone."
            },
            {
                "role": "user",
                "content": f"Generate a premise that includes the required elements to outline the story's foundation, based on the story idea '{story_idea}' and the tone '{tone}'."
            }
        ]
        return self.generate_content(premise_prompt, 'premise.txt')

    def generate_title(self, premise, story_idea, tone):
        title_prompt = [
            {
                "role": "system",
                "content": "You are an expert in crafting intriguing titles for stories. Please provide the title in the format: Title: <title_placeholder>. you only output the title."
            },
            {
                "role": "user",
                "content": f"Write 1 perfect title for the book using the format Title: <title_placeholder>. based on the Given premise:\n\n '{premise}'.\n\n the story idea : \n'{story_idea}'.\ntone: '{tone}'."
            }
        ]
        return self.generate_content(title_prompt, 'title.txt')

    def generate_toc(self, premise, story_idea, tone, num_chapters):
        toc_prompt = [
            {
                "role": "system",
                "content": f"You are tasked with generating a table of contents for {num_chapters} chapters. An excellent table of contents provides clear, concise, and descriptive chapter titles that give readers a glimpse of the chapter's content while invoking curiosity. The titles should be consistent in tone and style, and they should align with the overarching theme of the story."
            },
            {
                "role": "user",
                "content": f"Please follow the format: Table of Content: Chapter 1: <Title>, Chapter 2: <Title>, ... up to {num_chapters} chapters. Generate this table based on the premise '{premise}', the story idea '{story_idea}', and the tone '{tone}'."
            }
        ]
        return self.generate_content(toc_prompt, 'toc.txt')

    def identify_content_types(self, toc, story_idea, premise, tone):
        # Directly pass the initial ToC as part of the prompt without splitting or altering it
        content_types_prompt = [
            {
                "role": "system",
                "content": ("You're tasked with enriching an existing table of contents by adding a brief content type description next to each chapter title. Your additions should provide insights into the key events or themes of each chapter without changing the original titles. Use the format: [Original Chapter Title] - [Content Type]. Focus on incorporating content types that reflect significant plot events, character development, and thematic elements, ensuring they align with the story's tone of '" + tone + "'. Be concise and avoid modifying the chapter titles.")
            },
            {
                "role": "user",
                "content": f"Below is the table of contents for a story based on the idea '{story_idea}', with a premise '{premise}', and a desired tone of '{tone}'. For each chapter, add a content type description next to the original title using the specified format. Ensure your additions enhance understanding of the chapter's focus without altering the titles.\n\n{toc}"
            }
        ]
        
        return self.generate_content(content_types_prompt, 'content_types.txt')


    def refine_content_types(self, content_types, premise, tone):
        refine_prompt = [
            {
                "role": "system",
                "content": ("Refine the initial content types to ensure a coherent narrative and depth. Focus on a logical sequence of events, natural character development, seamless integration of background information, and avoidance of unnecessary details. Maintain consistency with the tone: '" + tone + "'. Use bullet points or succinct phrases for clarity.")
            },
            {
                "role": "user",
                "content": "Given the initial content types:\n\n" + content_types + "\n\nand the premise '" + premise + "', refine and deepen the details for each chapter, using bullet points or succinct phrases. Adhere to the instructions."
            }
        ]
        return self.generate_content(refine_prompt, 'refined_content_types.txt')

    def deepen_narrative(self, refined_content_types, premise, tone):
        deepen_prompt = [
            {
                "role": "system",
                "content": ("Elevate the narrative by enriching the refined content types. Focus on expanding crucial plot points, introducing nuanced character dynamics, building tension and conflicts, and smoothly leading towards the climax and resolution. Ensure the details added are pertinent and impactful, and keep everything aligned with the tone: '" + tone + "'. Depth should add to the story's richness without becoming verbose. Maintain the format provided and enhance each chapter's narrative comprehensively.")
            },
            {
                "role": "user",
                "content": "Expand the narrative for each chapter using the refined content types:\n\n" + refined_content_types + "\n\nConsider the premise '" + premise + "' and the tone '" + tone + "' as you develop the story further. Add depth and detail to each chapter, following the guidelines above."
            }
        ]
        return self.generate_content(deepen_prompt, 'deepened_narrative.txt')

    def extract_chapters_regex(self):
        # construct the filepath to include the base directory
        filepath = os.path.join(self.base_dir, "deepened_narrative.txt")

        try:
            with open(filepath, "r") as file:
                content = file.read()
        except FileNotFoundError:
            print(f"File not found: {filepath}. Please check the file path.")
            return None

        # Define patterns in a sequence
        patterns = [
            # First pattern for more formal chapter headings
            r"[.-]?\s*(?:Chapter|Ch\.|Section|Part)\s+\d+:\s*.*?(?=(?:[.-]?\s*(?:Chapter|Ch\.|Section|Part)\s+\d+:|$))",
            # Second pattern for less formal chapter introductions
            r"\- Chapter\s+\d+:\s*.*?(?=\s*\- Chapter\s+\d+:|$)"
        ]

        chapters = []
        for pattern in patterns:
            # Attempt to find matches with the current pattern
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                # If matches are found with the current pattern, extend the chapters list
                chapters.extend(matches)
                break  # Break the loop if chapters are found

        # Check if no chapters were extracted with any of the patterns
        if not chapters:
            print("No chapters were extracted with the provided patterns. Exiting...")
            return None

        extracted_chapters = []
        for index, chapter_content in enumerate(chapters, start=1):
            filename = f"chapter_{index}.txt"
            self.save_to_file(filename, chapter_content.strip())  # saves each chapter in the base directory

        return extracted_chapters

    def generate_first_outline(self, premise, num_chapters):
        # Load any existing content for Chapter 1, if available
        chapter_content = self.load_from_file("chapter_1.txt")
        
        # prompt for generating a timeline-like outline for Chapter 1
        outline_prompt = [
            {
                "role": "system",
                "content": "Outline the key events in Chapter 1 using a concise timeline outtline events . Focus on pivotal moments that introduce characters, setting, and the initial conflict. Keep descriptions brief and to the point."
            },
            {
                "role": "user",
                "content": f"Chapter 1 content:\n\n{chapter_content}\n\nGenerate a concise outtline events that includes:\n\n- Event: Description (1-2 sentences)\n- Character introduction and development\n- Initial conflict introduction\n- Setting introduction\n\nEnsure clarity and brevity in each point."
            }
        ]


        # Generate and save the timeline-like outline for Chapter 1
        outline = self.generate_content(outline_prompt, 'outline_chapter_1.txt')
        return outline

    def generate_remaining_outlines(self, num_chapters):
        for i in range(2, num_chapters + 1):
            chapter_content_N = self.load_from_file(f"chapter_{i}.txt")
            previous_chapter_outline = self.load_from_file(f"outline_chapter_{i - 1}.txt")
            
            # prompt for timeline generation
            outline_prompt = [
                {
                    "role": "system",
                    "content": f"Create a concise timeline outline story only for for Chapter {i}, detailing how it progresses the story. Highlight new events, character arcs, and conflicts, ensuring no repetition from previous chapters."
                },
                {
                    "role": "user",
                    "content": f"Given Chapter {i}'s content:\n\n{chapter_content_N}\n\nCraft a focused timeline  outline events  covering:\n\n- Major events with brief descriptions\n- Character developments\n- New conflicts or escalations\n- Integration of themes\n\nReference from previous chapter's outline:\n\n{previous_chapter_outline}\n\nAim for succinctness and specificity."
                }
            ]

            # Generate and save the timeline-like outline for the current chapter
            self.generate_content(outline_prompt, f'outline_chapter_{i}.txt')
      
    def generate_first_chapter(self, tone):
        outline = self.load_from_file('outline_chapter_1.txt')
        prompt = [
            {
                "role": "system",
                "content": f"As an expert narrative writer, you are tasked with crafting the opening chapter of a novel. This chapter must embody a {tone} tone, capturing the essence of the story's beginning as outlined. Your objective is to transform the provided chapter outline into engaging and coherent narrative prose. Focus on developing the scenes, actions, dialogues, and character emotions detailed in the outline, ensuring a rich and immersive reading experience. The final output should present a seamless narrative that adheres closely to the outline, emphasizing storytelling over conversation or extraneous details."
            },
            {
                "role": "user",
                "content": f"Based on the outline provided below, write a detailed narrative for Chapter 1. The narrative should vividly bring the outline to life, aligning closely with both the story's premise and the specified {tone} tone. Your narrative should include only the story content as informed by the outline, without deviating into unrelated discussions or dialogue with the reader.\n\nOutline for Chapter 1:\n\n{outline}\n\n."
            }
        ]
        first_chapter = self.generate_content(prompt, 'chapter_01.txt')
        return first_chapter


    def generate_remaining_chapters(self, num_chapters, tone):
        chapters = []
        for i in range(2, num_chapters + 1):
            outline = self.load_from_file(f'outline_chapter_{i}.txt')
            
            prompt = [
                {
                    "role": "system",
                    "content": f"As a skilled narrative writer, your task is to write Chapter {i} of a novel, ensuring it is infused with a {tone} tone. This chapter must seamlessly continue the story from the previous chapters, based solely on the provided outline. Your goal is to craft a narrative that is engaging, coherent, and true to the story's established direction. Focus on narrative development - including scenes, character dynamics, and plot progression - as indicated in the outline. Ensure the narrative is self-contained and consistent with the story's overarching themes and character arcs."
                },
                {
                    "role": "user",
                    "content": f"Using the outline for Chapter {i} below, craft a detailed narrative that effectively continues the story. This narrative should adhere to the specified {tone} tone and align with the overarching story arc, without assuming additional context not present in the outline. Ensure the chapter contributes meaningfully to the narrative progression and character development outlined thus far.\n\nOutline for Chapter {i}:\n\n{outline}\n\n."
                }
            ]
            chapter_content = self.generate_content(prompt, f'chapter_{i:02d}.txt')  # Ensuring consistent file naming
            chapters.append(chapter_content)
        return chapters

    
    def get_user_feedback(self, content_type, content, context="", component_name=None):
        """Prompt the user for feedback on the generated content."""
        print(f"\n🧐 Here's the {content_type} we've crafted for you:\n")
        print(content)
            
        feedback = input(f"\n🤔 Thoughts on this {content_type}? If you have feedback or want a revision, let us know. Otherwise, type 'perfect' to move on: ").strip().lower()
        
        if feedback == 'perfect':
            if component_name:  # Delete feedback file if it exists
                feedback_file_path = os.path.join('feedback_files', f'{component_name}_feedback.txt')  # Assuming a 'feedback_files' directory
                if os.path.exists(feedback_file_path):
                    os.remove(feedback_file_path)
            return content
        else:
            print("\n🕵️‍♂️ Alright, let's sprinkle some more magic on this!")
            return self.revise_content(content, feedback, context, component_name)

    def revise_content(self, original_content, feedback, context, component_name=None):
        # Construct the new prompt
        prompt_content = [
            {
                "role": "system",
                "content": "You are a meticulous revision specialist, skilled in refining content based on feedback. Your primary goal is to enhance the original content while preserving its core essence. It's crucial to avoid chatbot-like behavior and only focus on the task of revision."
            },
            {
                "role": "user",
                "content": f"Given the detailed feedback: '{feedback}', and the context: '{context}', adeptly refine the following content without straying from the feedback's intent: '{original_content}'. Ensure the revised content is clear and concise without any additional commentary."
            }
        ]

        
        revised_content = self.call_openai_api(prompt_content)

        if component_name:  # Save the revised content in a feedback file
            feedback_file_path = os.path.join('feedback_files', f'{component_name}_feedback.txt')  # Assuming a 'feedback_files' directory
            with open(feedback_file_path, 'w', encoding='utf-8') as file:
                file.write(revised_content)

        return revised_content


    def compile_book(self, title, toc, chapters):
        compiled_content = f"Title: {title}\n\nTable of Contents:\n{toc}\n\n"

        for i, chapter in enumerate(chapters):
            compiled_content += f"\nChapter {i+1}:\n\n{chapter}\n"

        self.save_to_file('compiled_book.txt', compiled_content)

    def main(self):

        # Step 1: Gather Input
        story_idea = input("Alright genius, give me your groundbreaking story idea: ")
        tone = input("Now, how do you want it to feel? E.g., dark, romantic, cheesy...: ")
        num_chapters = int(input("How many chapters should we suffer through? "))
        

        # Choose mode: Auto or Manual
        mode = input("Should I just whip it up automatically ('Auto') or do you want to nitpick every detail ('Manual')? ").strip().lower()
        while mode not in ["auto", "manual"]:
            mode = input("Wasn't that simple? 'Auto' or 'Manual'. Try again, Sherlock: ").strip().lower()

        # Step 2: Generate Premise
        print("\nAlright, diving deep into the vast AI brain to get you a premise...")
        premise = self.generate_premise(story_idea, tone)
        if mode == 'manual':
            premise = self.get_user_feedback("premise", premise, "Your vague idea: " + story_idea)

        # Step 3: Generate Title
        print("\nAttempting to coin a title that does justice to your... unique idea.")
        title = self.generate_title(premise, story_idea, tone)
        if mode == 'manual':
            title = self.get_user_feedback("title", title)

        # Step 4: Generate Table of Contents
        print("\nChiseling out a table of contents... ")
        toc = self.generate_toc(premise, story_idea, tone, num_chapters)
        if mode == 'manual':
            toc = self.get_user_feedback("table of contents", toc, "Your premise (again): " + premise)

        # Step 5: Identify Content Types
        print("\nDeciphering the mysteries of each chapter... 🕵️")
        initial_content_types = self.identify_content_types(toc, story_idea, premise, tone)
        if mode == 'manual':
            initial_content_types = self.get_user_feedback("initial content types", initial_content_types, "Table of contents (I hope you remember): " + toc)

        refined_content_types = self.refine_content_types(initial_content_types, premise, tone)
        if mode == 'manual':
            refined_content_types = self.get_user_feedback("refined content types", refined_content_types, "The initial (not-so-perfect) types: " + initial_content_types)

        # Step 6: Deepen Narrative
        print("\nSprinkling some depth into this narrative... Let's not make it too shallow.")
        deepened_narrative = self.deepen_narrative(refined_content_types, premise, tone)
        if mode == 'manual':
            deepened_narrative = self.get_user_feedback("deepened narrative", deepened_narrative, "The refined (slightly better) content types: " + refined_content_types)

        # Step 7: Extract Chapters
        print("\nExtracting chapters... Let's hope they make some sense!")
        extracted_chapters = self.extract_chapters_regex()
        # No feedback here as it's a technical extraction

        # Step 8: Generate Chapter Outlines
        print("\nSketching the first chapter's outline... Fingers crossed it's legible!")
        self.generate_first_outline(premise,num_chapters)
        if mode == 'manual':
            for i in range(1, num_chapters + 1):  # Iterate through all chapters
                outline = self.load_from_file(f"outline_chapter_{i}.txt")
                outline = self.get_user_feedback(f"outline for chapter {i}", outline, "The premise that started it all: " + premise)

        print("\nWorking on the remaining outlines... Expecting some Picasso-level sketches!")
        self.generate_remaining_outlines(num_chapters)
        # Feedback is already incorporated in the loop above

        # Step 9: Generate First Chapter
        print("\nRolling out the red carpet for the first chapter... Drumroll, please!")
        first_chapter = self.generate_first_chapter(tone)
        if mode == 'manual':
            first_chapter = self.get_user_feedback("first chapter", first_chapter, "Your premise (in case you forgot): " + premise)

        # Step 10: Generate Remaining Chapters
        print("\nSummoning the... chapters. Hope they're as interesting as you think!")
        remaining_chapters = self.generate_remaining_chapters(num_chapters, tone)
        if mode == 'manual':
            for i, chapter in enumerate(remaining_chapters, 2):  # Start from chapter 2
                print(f"\nAlright, critique chapter {i} if you must...")
                remaining_chapters[i-2] = self.get_user_feedback(f"chapter {i}", chapter, "Your premise: " + premise)

        # Step 11: Compile Book
        print("\nStitching it all together. Fingers crossed!")
        all_chapters = [first_chapter] + remaining_chapters
        self.compile_book(title, toc, all_chapters)

        print("\nVoilà! Your masterpiece is ready. (Or so you think!) Enjoy reading it and... good luck!")


if __name__ == "__main__":
    generator = StoryGenerator()
    generator.setup_project()