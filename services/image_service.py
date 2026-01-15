
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

    def generate_image(self, prompt: str) -> str:
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
