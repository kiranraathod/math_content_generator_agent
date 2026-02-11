
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
        self.model_name = "imagen-4.0-ultra-generate-001" 

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

    def generate_lesson_visual(self, lesson_title: str, heading: str, content: str, 
                               reference_image: Image.Image = None) -> Image.Image:
        """
        Generate a lesson visual using gemini-3-pro-image-preview with reference image support.
        
        Uses Google's generate_content API directly with the reference image passed inline.
        This avoids any chat serialization issues with Streamlit while leveraging Gemini 3 Pro's
        native ability to understand and replicate visual style from reference images.
        
        Args:
            lesson_title: Title of the lesson
            heading: Screen heading  
            content: Screen content body
            reference_image: Optional previous image to enforce visual consistency
            
        Returns:
            PIL Image object
        """
        screen_text = f"{heading} - {content}"
        
        try:
            if reference_image:
                # CONSISTENCY MODE: Pass reference image + strict consistency instructions
                logger.info("🎨 Generating with reference image for visual consistency...")
                consistency_prompt = (
                    f"I'm creating a series of illustrations for a children's math lesson called '{lesson_title}'. "
                    f"Here is the MASTER REFERENCE IMAGE that defines the visual identity for this lesson. "
                    f"You MUST generate a NEW illustration that: "
                    f"1. Uses the EXACT SAME main character/subject from the reference — identical shape, colors, proportions, and design. "
                    f"2. Keeps the EXACT SAME art style — line weight, shading technique, color palette, background style. "
                    f"3. Only changes the character's POSE and the SCENE CONTEXT to match this new scenario: '{screen_text[:300]}'. "
                    f"Think of this like drawing the next frame in an animation — the character must be recognizably the same. "
                    f"Do NOT add any text, numbers, or letters in the image. "
                    f"Do NOT change the art style or introduce new characters."
                )
                contents = [consistency_prompt, reference_image]
            else:
                # FIRST IMAGE: Establish the visual identity
                logger.info("🎨 Generating first image (establishing visual identity)...")
                first_prompt = (
                    f"Create a single iconic character or mascot for a children's math lesson called '{lesson_title}'. "
                    f"This character will be reused in ALL subsequent illustrations for this lesson. "
                    f"Design it to be: simple, distinctive, and EASY TO REPLICATE consistently across multiple images. "
                    f"Scene: {screen_text[:300]}. "
                    f"Art Style: Flat geometric vector art, rounded edges, simple shapes, no black outlines. "
                    f"Color Palette: bright and friendly. White background. "
                    f"Composition: Clean, minimalist, whimsical but mature. "
                    f"Do NOT add any text, numbers, or letters in the image."
                )
                contents = [first_prompt]
            
            response = self.client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE'],
                )
            )
            
            # Extract image from response - part.as_image() returns a GenAI SDK Image, not PIL
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    try:
                        genai_img = part.as_image()
                        if genai_img:
                            # Convert GenAI SDK Image (Pydantic) to PIL Image for Streamlit
                            pil_img = Image.open(io.BytesIO(genai_img.image_bytes))
                            logger.info("✅ Successfully generated image with gemini-3-pro-image-preview")
                            return pil_img
                    except Exception:
                        # This part is text, not image — skip it
                        continue
            
            logger.warning("No image found in gemini-3-pro-image-preview response.")
            return None
            
        except Exception as e:
            logger.error(f"gemini-3-pro-image-preview generation failed: {e}")
            raise e

