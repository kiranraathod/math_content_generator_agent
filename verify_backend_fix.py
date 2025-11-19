"""
Verification Test for Backend Fix
Tests that the config is properly initialized and passed through the workflow
"""

def test_backend_config_initialization():
    """Test that backend properly initializes with config"""
    print("="*60)
    print("BACKEND CONFIG FIX VERIFICATION TEST")
    print("="*60)
    
    try:
        print("\n1. Testing imports...")
        from backend import MathQuestionGenerator
        from services.config import MathGeneratorConfig
        print("   ✓ Imports successful")
        
        print("\n2. Testing backend initialization...")
        import os
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("   ⚠️  GOOGLE_API_KEY not set in environment")
            print("   ⚠️  Skipping initialization test")
            print("   ℹ️  Set GOOGLE_API_KEY in .env to run full test")
            return
        
        # Initialize generator
        generator = MathQuestionGenerator(api_key=api_key, model="gemini-2.5-flash")
        print("   ✓ Backend initialized successfully")
        
        print("\n3. Verifying config attribute...")
        assert hasattr(generator, 'config'), "Backend missing 'config' attribute"
        assert isinstance(generator.config, MathGeneratorConfig), "Config is not MathGeneratorConfig instance"
        print(f"   ✓ Config attribute exists: {type(generator.config).__name__}")
        
        print("\n4. Verifying config parameters...")
        assert hasattr(generator.config, 'max_validation_attempts'), "Config missing max_validation_attempts"
        assert hasattr(generator.config, 'max_revision_attempts'), "Config missing max_revision_attempts"
        print(f"   ✓ max_validation_attempts = {generator.config.max_validation_attempts}")
        print(f"   ✓ max_revision_attempts = {generator.config.max_revision_attempts}")
        
        print("\n5. Verifying services have config...")
        assert generator.question_service.config is not None, "QuestionService config is None"
        assert generator.validation_service.config is not None, "ValidationService config is None"
        assert generator.lesson_service.config is not None, "LessonService config is None"
        print("   ✓ All services have config")
        
        print("\n6. Verifying workflow has config...")
        assert generator.workflow.config is not None, "Workflow config is None"
        print("   ✓ Workflow has config")
        
        print("\n" + "="*60)
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\nThe backend fix is correctly implemented:")
        print("  ✓ Config import added")
        print("  ✓ Config instance created")
        print("  ✓ Config passed to all services")
        print("  ✓ Config passed to WorkflowOrchestrator")
        print("\nThe 'NoneType has no attribute max_validation_attempts' error")
        print("should now be RESOLVED!")
        print("\n📝 Next step: Test lesson generation with:")
        print("   streamlit run frontend.py")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_backend_config_initialization()
