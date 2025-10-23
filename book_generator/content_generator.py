import os
import re
from .api_client import ApiClient
from .file_utils import load_from_file, save_to_file

class ContentGenerator:
    def __init__(self, api_client, base_dir):
        self.api_client = api_client
        self.base_dir = base_dir

    def generate_content(self, prompt, filename):
        content = load_from_file(self.base_dir, filename)
        if content is None:
            content = self.api_client.call_openai_api(prompt)
            save_to_file(self.base_dir, filename, content)
        return content

    def generate_premise(self, story_idea, tone):
        premise_prompt = [
            {
                "role": "system",
                "content": "You are a master storyteller and narrative designer. Your task is to forge a compelling premise from a core idea. A strong premise must include: (1) a protagonist defined by a compelling adjective and role, (2) their specific, tangible goal, (3) the primary obstacle or crisis they face, and (4) a unique element or 'hook' that makes the story stand out. The premise must be concise, impactful, and clearly reflect the specified tone."
            },
            {
                "role": "user",
                "content": f"Analyze the following story idea and distill it into a powerful premise. Ensure all four required elements are present. Story Idea: '{story_idea}'. Tone: '{tone}'."
            }
        ]
        return self.generate_content(premise_prompt, 'premise.txt')

    def generate_title(self, premise, story_idea, tone):
        title_prompt = [
            {
                "role": "system",
                "content": "You are a renowned book editor with a knack for creating bestselling titles. Your task is to generate a single, powerful title for a book. The title must be evocative, genre-appropriate, and memorable. It should encapsulate the core essence of the premise and tone. Your output must be only the title, formatted as: Title: <Your Title>"
            },
            {
                "role": "user",
                "content": f"Based on the following premise, story idea, and tone, craft the perfect title. Premise:\n\n'{premise}'.\n\nStory Idea:\n'{story_idea}'.\nTone: '{tone}'."
            }
        ]
        return self.generate_content(title_prompt, 'title.txt')

    def generate_toc(self, premise, story_idea, tone, num_chapters):
        toc_prompt = [
            {
                "role": "system",
                "content": f"You are a developmental editor, skilled in structuring compelling narratives. Your task is to create a table of contents for a {num_chapters}-chapter book. The chapter titles must illustrate a clear narrative arc, showing progression from an inciting incident through rising action to a climax and resolution. Each title should be concise, intriguing, and consistent with the story's overall tone."
            },
            {
                "role": "user",
                "content": f"Generate a table of contents with {num_chapters} chapter titles. The structure should follow a logical narrative progression. Use the standard format: Table of Content: Chapter 1: <Title>, Chapter 2: <Title>, ...\n\nPremise: '{premise}'\nStory Idea: '{story_idea}'\nTone: '{tone}'."
            }
        ]
        return self.generate_content(toc_prompt, 'toc.txt')

    def identify_content_types(self, toc, story_idea, premise, tone):
        content_types_prompt = [
            {
                "role": "system",
                "content": ("You are a story analyst, expert at deconstructing narratives into their core components. Your task is to assign a key narrative event (e.g., 'Inciting Incident', 'Rising Action', 'Midpoint', 'Climax', 'Resolution') to each chapter title in the provided table of contents. This will serve as a structural backbone for the story. Use the format: [Original Chapter Title] - [Narrative Event]. Ensure your assignments create a coherent and compelling story structure that matches the specified tone."
                )
            },
            {
                "role": "user",
                "content": f"Analyze the table of contents below. For each chapter, append a key narrative event that reflects its role in the story's structure. Adhere to the specified format. The story is based on the premise '{premise}' and has a '{tone}' tone.\n\n{toc}"
            }
        ]

        return self.generate_content(content_types_prompt, 'content_types.txt')


    def refine_content_types(self, content_types, premise, tone):
        refine_prompt = [
            {
                "role": "system",
                "content": ("You are a senior narrative editor, refining a story's structure for maximum impact. Your task is to expand upon the initial chapter content types by adding specific key events and character beats for each chapter. For each chapter, list the critical plot points and character development moments that must occur. Use concise bullet points. This detailed outline must be consistent with the story's premise and tone."
                )
            },
            {
                "role": "user",
                "content": "Given the initial content types:\n\n" + content_types + "\n\nand the premise '" + premise + "', provide a detailed breakdown of key events and character beats for each chapter. Use bullet points for clarity. The tone is '" + tone + "'."
            }
        ]
        return self.generate_content(refine_prompt, 'refined_content_types.txt')

    def deepen_narrative(self, refined_content_types, premise, tone):
        deepen_prompt = [
            {
                "role": "system",
                "content": ("You are a world-class ghostwriter, transforming a detailed outline into a rich narrative summary. Your task is to synthesize the refined content types into a single, cohesive narrative. This text should read like a detailed summary or treatment of the entire story, flowing logically from one chapter's events to the next. This is not the final prose, but a comprehensive blueprint for it. Ensure the narrative is engaging and maintains the specified tone throughout."
                )
            },
            {
                "role": "user",
                "content": "Expand the following chapter-by-chapter breakdown into a single, continuous narrative summary. The summary must be detailed, coherent, and true to the premise and tone.\n\nRefined Content Types:\n" + refined_content_types + "\n\nPremise: '" + premise + "'\nTone: '" + tone + "'."
            }
        ]
        return self.generate_content(deepen_prompt, 'deepened_narrative.txt')

    def extract_chapters_regex(self):
        filepath = os.path.join(self.base_dir, "deepened_narrative.txt")
        try:
            with open(filepath, "r") as file:
                content = file.read()
        except FileNotFoundError:
            print(f"File not found: {filepath}. Please check the file path.")
            return None
        patterns = [
            r"[.-]?\s*(?:Chapter|Ch\.|Section|Part)\s+\d+:\s*.*?(?=(?:[.-]?\s*(?:Chapter|Ch\.|Section|Part)\s+\d+:|$))",
            r"\- Chapter\s+\d+:\s*.*?(?=\s*\- Chapter\s+\d+:|$)"
        ]
        chapters = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                chapters.extend(matches)
                break
        if not chapters:
            print("No chapters were extracted with the provided patterns. Exiting...")
            return None
        for index, chapter_content in enumerate(chapters, start=1):
            filename = f"chapter_{index}.txt"
            save_to_file(self.base_dir, filename, chapter_content.strip())
        return chapters

    def generate_first_outline(self, premise, num_chapters):
        chapter_content = load_from_file(self.base_dir, "chapter_1.txt")
        outline_prompt = [
            {
                "role": "system",
                "content": "You are a meticulous outliner, skilled at creating a detailed scene-by-scene roadmap for a story. Your task is to analyze the provided chapter summary and break it down into a concise, timeline-style outline. Focus on pivotal moments, character actions, and key dialogue. Each point should be a clear, actionable event."
            },
            {
                "role": "user",
                "content": f"Based on the following chapter summary, generate a concise, timeline-style outline of key events.\n\nChapter 1 Summary:\n\n{chapter_content}\n\nEnsure clarity and brevity in each point."
            }
        ]
        return self.generate_content(outline_prompt, 'outline_chapter_1.txt')

    def generate_remaining_outlines(self, num_chapters):
        for i in range(2, num_chapters + 1):
            chapter_content_N = load_from_file(self.base_dir, f"chapter_{i}.txt")
            previous_chapter_outline = load_from_file(self.base_dir, f"outline_chapter_{i - 1}.txt")
            outline_prompt = [
                {
                    "role": "system",
                    "content": f"You are a meticulous outliner, continuing the scene-by-scene roadmap for a story. Your task is to create a concise timeline outline for Chapter {i}. It must logically follow the previous chapter's outline, highlighting new events, character developments, and escalating conflicts. Do not repeat events from the previous outline."
                },
                {
                    "role": "user",
                    "content": f"Given the summary for Chapter {i}:\n\n{chapter_content_N}\n\nAnd the outline for the previous chapter:\n\n{previous_chapter_outline}\n\nCraft a focused timeline of events for Chapter {i}. Aim for succinctness and specificity."
                }
            ]
            self.generate_content(outline_prompt, f'outline_chapter_{i}.txt')

    def generate_first_chapter(self, tone):
        outline = load_from_file(self.base_dir, 'outline_chapter_1.txt')
        prompt = [
            {
                "role": "system",
                "content": f"You are a master prose stylist and fiction author. Your task is to write the full text of an opening chapter from a detailed outline. Embody the specified '{tone}' tone in every sentence. Focus on vivid descriptions, compelling character voice, and engaging pacing. Your writing should 'show, don't tell,' immersing the reader in the world. The final output must be only the narrative prose of the chapter, without any additional commentary."
            },
            {
                "role": "user",
                "content": f"From the outline below, write the full narrative for Chapter 1. The prose must be engaging, adhere to the '{tone}' tone, and bring the outlined events to life.\n\nOutline for Chapter 1:\n\n{outline}"
            }
        ]
        return self.generate_content(prompt, 'chapter_01.txt')


    def generate_remaining_chapters(self, num_chapters, tone):
        chapters = []
        for i in range(2, num_chapters + 1):
            outline = load_from_file(self.base_dir, f'outline_chapter_{i}.txt')

            prompt = [
                {
                    "role": "system",
                    "content": f"You are a master prose stylist and fiction author, continuing a novel. Your task is to write Chapter {i} from its outline, ensuring it maintains the established '{tone}' tone and seamlessly continues the narrative from the previous chapter. Focus on vivid descriptions, consistent character voice, and compelling pacing. The output must be only the narrative prose."
                },
                {
                    "role": "user",
                    "content": f"From the outline below, write the full narrative for Chapter {i}. The prose must be engaging, adhere to the '{tone}' tone, and logically follow the events of the preceding chapters.\n\nOutline for Chapter {i}:\n\n{outline}"
                }
            ]
            chapter_content = self.generate_content(prompt, f'chapter_{i:02d}.txt')
            chapters.append(chapter_content)
        return chapters
