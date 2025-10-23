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
                "content": "Outline the key events in Chapter 1 using a concise timeline outtline events . Focus on pivotal moments that introduce characters, setting, and the initial conflict. Keep descriptions brief and to the point."
            },
            {
                "role": "user",
                "content": f"Chapter 1 content:\n\n{chapter_content}\n\nGenerate a concise outtline events that includes:\n\n- Event: Description (1-2 sentences)\n- Character introduction and development\n- Initial conflict introduction\n- Setting introduction\n\nEnsure clarity and brevity in each point."
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
                    "content": f"Create a concise timeline outline story only for for Chapter {i}, detailing how it progresses the story. Highlight new events, character arcs, and conflicts, ensuring no repetition from previous chapters."
                },
                {
                    "role": "user",
                    "content": f"Given Chapter {i}'s content:\n\n{chapter_content_N}\n\nCraft a focused timeline  outline events  covering:\n\n- Major events with brief descriptions\n- Character developments\n- New conflicts or escalations\n- Integration of themes\n\nReference from previous chapter's outline:\n\n{previous_chapter_outline}\n\nAim for succinctness and specificity."
                }
            ]
            self.generate_content(outline_prompt, f'outline_chapter_{i}.txt')

    def generate_first_chapter(self, tone):
        outline = load_from_file(self.base_dir, 'outline_chapter_1.txt')
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
        return self.generate_content(prompt, 'chapter_01.txt')

    def generate_remaining_chapters(self, num_chapters, tone):
        chapters = []
        for i in range(2, num_chapters + 1):
            outline = load_from_file(self.base_dir, f'outline_chapter_{i}.txt')
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
            chapter_content = self.generate_content(prompt, f'chapter_{i:02d}.txt')
            chapters.append(chapter_content)
        return chapters
