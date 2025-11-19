"""Temporary script to update models.py with lesson fields"""

models_file = r'C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\models.py'

# Read the file
with open(models_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add generate_lesson to InputState
content = content.replace(
    '    level: int\n\n\nclass OutputState',
    '    level: int\n    generate_lesson: Optional[bool]\n\n\nclass OutputState'
)

# Add lesson fields to OutputState
content = content.replace(
    '    # MCQ-specific fields (optional)\n    options: Optional[List[str]]\n    correct_option: Optional[str]\n\n\nclass QuestionState',
    '''    # MCQ-specific fields (optional)
    options: Optional[List[str]]
    correct_option: Optional[str]
    # Lesson fields (optional)
    lesson_title: Optional[str]
    lesson_introduction: Optional[str]
    real_world_example: Optional[str]
    key_concepts: Optional[List[str]]
    definitions: Optional[str]
    practice_tips: Optional[str]


class QuestionState'''
)

# Add lesson fields to QuestionState attributes
content = content.replace(
    '    # MCQ-specific fields (optional)\n    options: List[str]\n    correct_option: str',
    '''    # MCQ-specific fields (optional)
    options: List[str]
    correct_option: str
    
    # Lesson fields (optional)
    generate_lesson: bool
    lesson_title: str
    lesson_introduction: str
    real_world_example: str
    key_concepts: List[str]
    definitions: str
    practice_tips: str'''
)

# Update docstring
content = content.replace(
    '        use_examples: Whether to fetch and include database examples in prompt\n        \n        # Output fields',
    '''        use_examples: Whether to fetch and include database examples in prompt
        generate_lesson: Whether to generate a lesson (NEW)
        
        # Output fields'''
)

content = content.replace(
    '        options: List of 4 multiple choice options (for MCQ type only)\n        correct_option: The correct option letter A, B, C, or D (for MCQ type only)\n        \n        # Internal processing fields',
    '''        options: List of 4 multiple choice options (for MCQ type only)
        correct_option: The correct option letter A, B, C, or D (for MCQ type only)
        
        # Lesson fields (NEW)
        lesson_title: Title of the generated lesson
        lesson_introduction: Introduction to the lesson
        real_world_example: Real-world example with emojis
        key_concepts: List of key concepts
        definitions: Important definitions
        practice_tips: Tips for mastering the topic
        
        # Internal processing fields'''
)

# Write back
with open(models_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated models.py with lesson fields")
