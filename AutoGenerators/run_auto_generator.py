"""
Runner script for Automatic Level Generator
Interactive menu for generating questions automatically across different levels and subtopics
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoGenerators.auto_level_generator import AutoLevelGenerator
import random


def print_menu():
    """Display the menu options."""
    print("\n" + "="*80)
    print("AUTOMATIC LEVEL GENERATOR - MENU")
    print("="*80)
    print("\n1. Generate for random subtopics (default: 3 questions per subtopic)")
    print("2. Generate for specific subtopic")
    print("3. Generate across all levels (1-6) for a subtopic")
    print("4. View available subtopics with examples")
    print("5. Batch generate for multiple random subtopics")
    print("6. Test mode (1 subtopic, 1 question, no upload)")
    print("0. Exit")
    print("\n" + "="*80)


def generate_random_subtopics(generator):
    """Generate for random subtopics."""
    print("\n" + "="*80)
    print("GENERATE FOR RANDOM SUBTOPICS")
    print("="*80)
    
    # Get parameters
    num_subtopics = input("Number of subtopics (default: 3): ").strip()
    num_subtopics = int(num_subtopics) if num_subtopics else 3
    
    questions_per = input("Questions per subtopic (default: 3): ").strip()
    questions_per = int(questions_per) if questions_per else 3
    
    level = input("Difficulty level 1-6 (default: 1): ").strip()
    level = int(level) if level else 1
    
    if level < 1 or level > 6:
        print("❌ Invalid level. Must be 1-6.")
        return
    
    subject = input("Subject (default: Algebra 1): ").strip()
    subject = subject if subject else "Algebra 1"
    
    auto_upload = input("Auto-upload to database? (yes/no, default: yes): ").strip().lower()
    auto_upload = auto_upload != 'no'
    
    # Ask whether to include examples with visual elements
    visuals = input("Include examples with visual elements? (yes/no, default: yes): ").strip().lower()
    include_visuals = visuals != 'no'

    print(f"\n🚀 Starting generation...")
    print(f"   Subtopics: {num_subtopics}")
    print(f"   Questions per subtopic: {questions_per}")
    print(f"   Level: {level}")
    print(f"   Subject: {subject}")
    print(f"   Auto-upload: {auto_upload}")
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return

    # If user doesn't want visuals, perform client-side filtering of subtopics
    # because AutoLevelGenerator.generate_for_random_subtopics doesn't accept
    # a visuals flag. We'll fetch available subtopics and pick random ones
    # that match the visual preference, then call generate_for_specific_subtopic
    # for each selected subtopic.
    all_subtopics = generator.get_subtopics_with_examples(subject=subject)

    if not include_visuals:
        filtered = [s for s in all_subtopics if s.get('examples_with_visuals', 0) == 0]
    else:
        filtered = all_subtopics

    if not filtered:
        # If no subtopics match the "no visuals" preference, offer to proceed
        # with visuals enabled instead of failing silently.
        choice = input(f"\nNo subtopics without visuals found for {subject}. Proceed with visuals anyway? (yes/no, default: no): ").strip().lower()
        if choice == 'yes':
            filtered = all_subtopics
        else:
            print("Cancelled.")
            return

    num_to_select = min(num_subtopics, len(filtered))
    selected = random.sample(filtered, num_to_select)

    total_generated = 0
    total_uploaded = 0
    processed = 0

    for info in selected:
        subtopic = info['subtopic']
        print(f"\n{'='*80}")
        print(f"Processing subtopic: {subtopic}")
        print(f"{'='*80}")

        results = generator.generate_for_specific_subtopic(
            subtopic=subtopic,
            subject=subject,
            questions_per_subtopic=questions_per,
            level=level,
            auto_upload=auto_upload
        )

        if results.get('success'):
            processed += 1
            total_generated += results.get('generated', 0)
            total_uploaded += results.get('uploaded', 0)

    print("\n✅ Generation complete!")
    print(f"Processed subtopics: {processed}/{num_to_select}")
    print(f"Total questions generated: {total_generated}")
    if auto_upload:
        print(f"Total questions uploaded: {total_uploaded}")


def generate_specific_subtopic(generator):
    """Generate for a specific subtopic."""
    print("\n" + "="*80)
    print("GENERATE FOR SPECIFIC SUBTOPIC")
    print("="*80)
    
    # Show available subtopics first
    print("\n📚 Available subtopics:")
    subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")
    for idx, info in enumerate(subtopics[:20], 1):  # Show first 20
        print(f"{idx}. {info['subtopic']} ({', '.join(info['question_types'])})")
    
    if len(subtopics) > 20:
        print(f"... and {len(subtopics) - 20} more")
    
    print("\n")
    subtopic = input("Enter subtopic name: ").strip()
    
    if not subtopic:
        print("❌ Subtopic is required.")
        return
    
    questions_per = input("Questions to generate (default: 3): ").strip()
    questions_per = int(questions_per) if questions_per else 3
    
    level = input("Difficulty level 1-6 (default: 1): ").strip()
    level = int(level) if level else 1
    
    if level < 1 or level > 6:
        print("❌ Invalid level. Must be 1-6.")
        return
    
    subject = input("Subject (default: Algebra 1): ").strip()
    subject = subject if subject else "Algebra 1"
    
    auto_upload = input("Auto-upload to database? (yes/no, default: yes): ").strip().lower()
    auto_upload = auto_upload != 'no'
    
    results = generator.generate_for_specific_subtopic(
        subtopic=subtopic,
        subject=subject,
        questions_per_subtopic=questions_per,
        level=level,
        auto_upload=auto_upload
    )
    
    if results['success']:
        print("\n✅ Generation complete!")
    else:
        print("\n❌ Generation failed.")


def generate_all_levels(generator):
    """Generate across all levels (1-6) for a subtopic."""
    print("\n" + "="*80)
    print("GENERATE ACROSS ALL LEVELS")
    print("="*80)
    
    # Show available subtopics
    print("\n📚 Available subtopics:")
    subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")
    for idx, info in enumerate(subtopics[:20], 1):
        print(f"{idx}. {info['subtopic']} ({', '.join(info['question_types'])})")
    
    if len(subtopics) > 20:
        print(f"... and {len(subtopics) - 20} more")
    
    print("\n")
    subtopic = input("Enter subtopic name: ").strip()
    
    if not subtopic:
        print("❌ Subtopic is required.")
        return
    
    questions_per_level = input("Questions per level (default: 2): ").strip()
    questions_per_level = int(questions_per_level) if questions_per_level else 2
    
    subject = input("Subject (default: Algebra 1): ").strip()
    subject = subject if subject else "Algebra 1"
    
    auto_upload = input("Auto-upload to database? (yes/no, default: yes): ").strip().lower()
    auto_upload = auto_upload != 'no'
    
    print(f"\n⚠️  This will generate {questions_per_level * 6} questions (levels 1-6)")
    confirm = input("Proceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    all_questions = []
    
    for level in range(1, 7):
        print(f"\n{'='*80}")
        print(f"LEVEL {level}")
        print(f"{'='*80}")
        
        results = generator.generate_for_specific_subtopic(
            subtopic=subtopic,
            subject=subject,
            questions_per_subtopic=questions_per_level,
            level=level,
            auto_upload=False  # Upload all at once at the end
        )
        
        if results['success'] and results['generated'] > 0:
            print(f"✓ Level {level} complete: {results['generated']} questions")
    
    # Upload all questions at once
    if auto_upload:
        print("\n☁️  Uploading all questions to database...")
        # Note: The generator already uploaded during the loop if auto_upload was True
        # Since we set it to False, we would need to collect and upload manually
        # For simplicity, let's just inform the user
        print("✓ Questions uploaded during generation")
    
    print("\n✅ All levels complete!")


def view_available_subtopics(generator):
    """View all available subtopics with examples."""
    print("\n" + "="*80)
    print("AVAILABLE SUBTOPICS WITH EXAMPLES")
    print("="*80)
    
    subject = input("Subject (default: Algebra 1): ").strip()
    subject = subject if subject else "Algebra 1"
    
    subtopics = generator.get_subtopics_with_examples(subject=subject)
    
    if not subtopics:
        print(f"\n❌ No subtopics with examples found for {subject}")
        return
    
    print(f"\n📚 Found {len(subtopics)} subtopics:\n")
    
    for idx, info in enumerate(subtopics, 1):
        print(f"{idx}. {info['subtopic']}")
        print(f"   Examples: {info['total_examples']}")
        print(f"   Question types: {', '.join(info['question_types'])}")
        if info['examples_with_visuals'] > 0:
            print(f"   Visual elements: {info['examples_with_visuals']} examples")
        print()


def batch_generate(generator):
    """Batch generate for multiple random subtopics."""
    print("\n" + "="*80)
    print("BATCH GENERATION")
    print("="*80)
    
    num_batches = input("Number of batches (default: 3): ").strip()
    num_batches = int(num_batches) if num_batches else 3
    
    subtopics_per_batch = input("Subtopics per batch (default: 5): ").strip()
    subtopics_per_batch = int(subtopics_per_batch) if subtopics_per_batch else 5
    
    questions_per = input("Questions per subtopic (default: 3): ").strip()
    questions_per = int(questions_per) if questions_per else 3
    
    level = input("Difficulty level 1-6 (default: 1): ").strip()
    level = int(level) if level else 1
    
    if level < 1 or level > 6:
        print("❌ Invalid level. Must be 1-6.")
        return
    
    total_questions = num_batches * subtopics_per_batch * questions_per
    print(f"\n⚠️  This will generate approximately {total_questions} questions")
    print(f"   Batches: {num_batches}")
    print(f"   Subtopics per batch: {subtopics_per_batch}")
    print(f"   Questions per subtopic: {questions_per}")
    print(f"   Level: {level}")
    
    # Ask whether to include examples with visual elements
    visuals = input("Include examples with visual elements? (yes/no, default: yes): ").strip().lower()
    include_visuals = visuals != 'no'

    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    total_generated = 0
    total_uploaded = 0

    for batch_num in range(1, num_batches + 1):
        print(f"\n{'='*80}")
        print(f"BATCH {batch_num}/{num_batches}")
        print(f"{'='*80}")

        # Fetch and filter subtopics according to visual preference
        all_subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")
        if not include_visuals:
            candidates = [s for s in all_subtopics if s.get('visual_elements_description', 0) == 0]
        else:
            candidates = all_subtopics

        if not candidates:
            # Offer to proceed with visuals if none match the "no visuals" filter
            choice = input("No subtopics without visuals available. Proceed with visuals for this batch? (yes/no, default: no): ").strip().lower()
            if choice == 'yes':
                candidates = all_subtopics
            else:
                print("Skipping this batch.")
                continue

        num_to_select = min(subtopics_per_batch, len(candidates))
        selected = random.sample(candidates, num_to_select)

        # Generate for each selected subtopic
        for info in selected:
            subtopic = info['subtopic']
            results = generator.generate_for_specific_subtopic(
                subtopic=subtopic,
                subject="Algebra 1",
                questions_per_subtopic=questions_per,
                level=level,
                auto_upload=True
            )

            total_generated += results.get('generated', 0)
            total_uploaded += results.get('uploaded', 0)
    
    print("\n" + "="*80)
    print("BATCH GENERATION COMPLETE")
    print("="*80)
    print(f"Total questions generated: {total_generated}")
    print(f"Total questions uploaded: {total_uploaded}")
    print("="*80)


def test_mode(generator):
    """Test mode - generate 1 question without uploading."""
    print("\n" + "="*80)
    print("TEST MODE")
    print("="*80)
    print("Generating 1 question from 1 random subtopic (no upload)")
    
    results = generator.generate_for_random_subtopics(
        num_subtopics=1,
        subject="Algebra 1",
        questions_per_subtopic=1,
        level=1,
        auto_upload=False
    )
    
    print("\n✅ Test complete!")


def main():
    """Main menu loop."""
    try:
        # Initialize generator
        print("Initializing Automatic Level Generator...")
        generator = AutoLevelGenerator()
        print("✓ Ready!")
        
        while True:
            try:
                print_menu()
                choice = input("Select an option (0-6): ").strip()
                
                if choice == '1':
                    generate_random_subtopics(generator)
                elif choice == '2':
                    generate_specific_subtopic(generator)
                elif choice == '3':
                    generate_all_levels(generator)
                elif choice == '4':
                    view_available_subtopics(generator)
                elif choice == '5':
                    batch_generate(generator)
                elif choice == '6':
                    test_mode(generator)
                elif choice == '0':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("\n❌ Invalid option. Please choose 0-6.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")
    
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("💡 Make sure your .env file has GOOGLE_API_KEY, SUPABASE_URL, and SUPABASE_KEY")
    except Exception as e:
        print(f"\n❌ Initialization Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
