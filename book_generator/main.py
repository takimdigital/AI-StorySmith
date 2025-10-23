import os
from book_generator.api_client import ApiClient
from book_generator.content_generator import ContentGenerator
from book_generator.user_interaction import UserInteraction
from book_generator.book_compiler import compile_book
from book_generator.file_utils import sanitize_filename, load_from_file

def main():
    # Step 1: Gather Input
    story_idea = input("Alright genius, give me your groundbreaking story idea: ")
    tone = input("Now, how do you want it to feel? E.g., dark, romantic, cheesy...: ")
    num_chapters = int(input("How many chapters should we suffer through? "))
    book_title = input("First things first, what's the title of your Folder name masterpiece? ")

    base_dir = os.path.join('generated_content', sanitize_filename(book_title))
    os.makedirs(base_dir, exist_ok=True)

    # Choose mode: Auto or Manual
    mode = input("Should I just whip it up automatically ('Auto') or do you want to nitpick every detail ('Manual')? ").strip().lower()
    while mode not in ["auto", "manual"]:
        mode = input("Wasn't that simple? 'Auto' or 'Manual'. Try again, Sherlock: ").strip().lower()

    # Initialize clients and generators
    api_client = ApiClient()
    content_generator = ContentGenerator(api_client, base_dir)
    user_interaction = UserInteraction(api_client)

    # Step 2: Generate Premise
    print("\nAlright, diving deep into the vast AI brain to get you a premise...")
    premise = content_generator.generate_premise(story_idea, tone)
    if mode == 'manual':
        premise = user_interaction.get_user_feedback("premise", premise, "Your vague idea: " + story_idea)

    # Step 3: Generate Title
    print("\nAttempting to coin a title that does justice to your... unique idea.")
    title = content_generator.generate_title(premise, story_idea, tone)
    if mode == 'manual':
        title = user_interaction.get_user_feedback("title", title)

    # Step 4: Generate Table of Contents
    print("\nChiseling out a table of contents... ")
    toc = content_generator.generate_toc(premise, story_idea, tone, num_chapters)
    if mode == 'manual':
        toc = user_interaction.get_user_feedback("table of contents", toc, "Your premise (again): " + premise)

    # Step 5: Identify Content Types
    print("\nDeciphering the mysteries of each chapter... 🕵️")
    initial_content_types = content_generator.identify_content_types(toc, story_idea, premise, tone)
    if mode == 'manual':
        initial_content_types = user_interaction.get_user_feedback("initial content types", initial_content_types, "Table of contents (I hope you remember): " + toc)

    refined_content_types = content_generator.refine_content_types(initial_content_types, premise, tone)
    if mode == 'manual':
        refined_content_types = user_interaction.get_user_feedback("refined content types", refined_content_types, "The initial (not-so-perfect) types: " + initial_content_types)

    # Step 6: Deepen Narrative
    print("\nSprinkling some depth into this narrative... Let's not make it too shallow.")
    deepened_narrative = content_generator.deepen_narrative(refined_content_types, premise, tone)
    if mode == 'manual':
        deepened_narrative = user_interaction.get_user_feedback("deepened narrative", deepened_narrative, "The refined (slightly better) content types: " + refined_content_types)

    # Step 7: Extract Chapters
    print("\nExtracting chapters... Let's hope they make some sense!")
    content_generator.extract_chapters_regex()

    # Step 8: Generate Chapter Outlines
    print("\nSketching the first chapter's outline... Fingers crossed it's legible!")
    content_generator.generate_first_outline(premise,num_chapters)
    if mode == 'manual':
        for i in range(1, num_chapters + 1):
            outline = load_from_file(base_dir, f"outline_chapter_{i}.txt")
            outline = user_interaction.get_user_feedback(f"outline for chapter {i}", outline, "The premise that started it all: " + premise)

    print("\nWorking on the remaining outlines... Expecting some Picasso-level sketches!")
    content_generator.generate_remaining_outlines(num_chapters)

    # Step 9: Generate First Chapter
    print("\nRolling out the red carpet for the first chapter... Drumroll, please!")
    first_chapter = content_generator.generate_first_chapter(tone)
    if mode == 'manual':
        first_chapter = user_interaction.get_user_feedback("first chapter", first_chapter, "Your premise (in case you forgot): " + premise)

    # Step 10: Generate Remaining Chapters
    print("\nSummoning the... chapters. Hope they're as interesting as you think!")
    remaining_chapters = content_generator.generate_remaining_chapters(num_chapters, tone)
    if mode == 'manual':
        for i, chapter in enumerate(remaining_chapters, 2):
            print(f"\nAlright, critique chapter {i} if you must...")
            remaining_chapters[i-2] = user_interaction.get_user_feedback(f"chapter {i}", chapter, "Your premise: " + premise)

    # Step 11: Compile Book
    print("\nStitching it all together. Fingers crossed!")
    all_chapters = [first_chapter] + remaining_chapters
    compile_book(base_dir, title, toc, all_chapters)

    print("\nVoilà! Your masterpiece is ready. (Or so you think!) Enjoy reading it and... good luck!")

if __name__ == "__main__":
    main()
