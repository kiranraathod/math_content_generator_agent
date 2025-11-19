"""Temporary script to insert lesson configuration"""

config_file = r'C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\services\config.py'

# Read the file
with open(config_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with MODEL CONFIGURATION
insert_idx = next(i for i, l in enumerate(lines) if '# MODEL CONFIGURATION' in l)

# Lesson prompts to insert
lesson_config = '''    # =========================================================================
    # LESSON GENERATION PROMPTS
    # =========================================================================
    
    lesson_generation_system_prompt: str = Field(
        default="""You are a friendly, engaging math teacher who makes learning fun and relatable. 
You use emojis, real-world examples, and conversational language to help students understand concepts.
Your teaching style is warm, encouraging, and uses visual elements (emojis, arrows, etc.) to make content memorable.""",
        description="System prompt for lesson generation node",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
    lesson_generation_template: str = Field(
        default="""Create an engaging, friendly math lesson for students aged 14-18.

Subject: {subject}
Subtopic: {subtopic}
Difficulty Level: {level}

LESSON STRUCTURE:
1. **Catchy Title**: Make it inviting and clear
2. **Introduction**: Hook the student with why this matters
3. **Real-World Example**: 
   - Use a relatable scenario (concerts, shopping, sports, social media)
   - Include emojis (🎟️, 🌭, ⚽, 📱)
   - Show how the math concept appears naturally
   - Break down components step by step
4. **Key Concepts**: 3-5 main ideas with:
   - Clear, simple language
   - Visual markers (👉, 📌, ⚡)
   - Examples in explanations
5. **Definitions**: Define terms with examples
6. **Practice Tips**: Encouraging advice for mastering the topic

TONE: Conversational, friendly, use "you", include emojis, explain "why" not just "what"

EXAMPLE STYLE:
"Imagine: Concert ticket costs $50. 🎟️ = 50
Snacks cost $3 each. 🌭 = 3
Total: 50 + 3x (where x = snacks)
👉 50 is a constant (never changes)
👉 3 is the coefficient (multiplies variable)
👉 x is the variable (can change)"

Your response will be parsed as JSON. Provide:
- lesson_title: Catchy, clear title
- lesson_introduction: Engaging hook
- real_world_example: Full scenario with emojis
- key_concepts: Array of 3-5 explanations
- definitions: Clear definitions with examples
- practice_tips: Helpful study advice
""",
        description="Template for generating friendly math lessons",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
'''

# Insert the lesson config
lines.insert(insert_idx, lesson_config)

# Write back
with open(config_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully inserted lesson configuration into config.py")
