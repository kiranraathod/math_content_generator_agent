
import logging
import io
from PIL import Image
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class ImageGeneratorService:
    """
    Service for generating images using Google's Imagen models via the google-genai SDK.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Image Generator Service.
        
        Args:
            api_key: Google API Key
        """
        if not api_key:
            raise ValueError("API Key is required for Image Generation")
            
        self.client = genai.Client(api_key=api_key)
        # Using the model that was verified to work with the key
        self.model_name = "imagen-4.0-fast-generate-001" 

    def generate_image(self, prompt: str) -> Image.Image:
        """
        Generate an image based on a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            
        Returns:
            PIL Image object.
        """
        try:
            logger.info(f"Generating image with prompt: {prompt[:50]}...")
            
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=prompt,
                config={
                    'number_of_images': 1,
                }
            )
            
            if response.generated_images:
                # Get Pydantic image object
                img_obj = response.generated_images[0].image
                # Convert bytes to PIL Image
                return Image.open(io.BytesIO(img_obj.image_bytes))
            else:
                logger.warning("No images returned from API")
                return None
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise e

    def generate_lesson_visual(self, lesson_title: str, heading: str, content: str) -> Image.Image:
        """
        Generate a specific lesson visual using the standardized prompt template.
        
        Args:
            lesson_title: Title of the lesson
            heading: Screen heading
            content: Screen content body
            
        Returns:
            PIL Image object
        """
        screen_text = f"{heading} - {content}"
        
        prompt = (
            f"A flat 2D vector illustration for a math lesson about {lesson_title}. "
            f"Visual Subject: A literal or metaphorical depiction of this scenario: '{screen_text[:300]}'. "
            f"Art Style: Flat geometric vector art, rounded edges, simple shapes, no black outlines. "
            f"Color Palette: Strictly limited—use 1 or 2 vibrant accent colors (like light blue or electric blue) "
            f"against a calm, neutral background (white/light gray). "
            f"Composition: Clean, minimalist, cute but mature."
        )
        
        return self.generate_image(prompt)
