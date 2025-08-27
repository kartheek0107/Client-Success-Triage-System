#!/usr/bin/env python3
"""
Debug script to find exactly where the null bytes issue occurs during imports.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("🔍 DEBUGGING IMPORT CHAIN")
print("=" * 50)
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")  # Show first 3 entries

def test_import_step_by_step():
    """Test each import step to isolate the null bytes issue."""
    
    print("\n1️⃣ Testing basic imports...")
    try:
        import re
        import string
        print("✅ Standard library imports: OK")
    except Exception as e:
        print(f"❌ Standard library error: {e}")
        return False
    
    print("\n2️⃣ Testing spaCy import...")
    try:
        import spacy
        print("✅ spaCy import: OK")
    except Exception as e:
        print(f"❌ spaCy error: {e}")
        return False
    
    print("\n3️⃣ Testing spaCy model loading...")
    try:
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loading: OK")
    except Exception as e:
        print(f"❌ spaCy model error: {e}")
        return False
    
    print("\n4️⃣ Testing nlp_pipeline package import...")
    try:
        import nlp_pipeline
        print("✅ nlp_pipeline package: OK")
    except Exception as e:
        print(f"❌ nlp_pipeline package error: {e}")
        return False
    
    print("\n5️⃣ Testing preprocessing subpackage import...")
    try:
        import nlp_pipeline.preprocessing
        print("✅ nlp_pipeline.preprocessing package: OK")
    except Exception as e:
        print(f"❌ nlp_pipeline.preprocessing error: {e}")
        return False
    
    print("\n6️⃣ Testing cleaner module import...")
    try:
        import nlp_pipeline.preprocessing.cleaner
        print("✅ cleaner module import: OK")
    except Exception as e:
        print(f"❌ cleaner module error: {e}")
        print(f"Error type: {type(e)}")
        return False
    
    print("\n7️⃣ Testing function imports...")
    try:
        from nlp_pipeline.preprocessing.cleaner import clean_text
        print("✅ clean_text import: OK")
    except Exception as e:
        print(f"❌ clean_text import error: {e}")
        return False
    
    try:
        from nlp_pipeline.preprocessing.cleaner import tokenize_and_lemmatize
        print("✅ tokenize_and_lemmatize import: OK")
    except Exception as e:
        print(f"❌ tokenize_and_lemmatize import error: {e}")
        return False
    
    try:
        from nlp_pipeline.preprocessing.cleaner import preprocess_text
        print("✅ preprocess_text import: OK")
    except Exception as e:
        print(f"❌ preprocess_text import error: {e}")
        return False
    
    print("\n8️⃣ Testing function execution...")
    try:
        result = preprocess_text("test message")
        print(f"✅ Function execution: OK (result: '{result}')")
    except Exception as e:
        print(f"❌ Function execution error: {e}")
        return False
    
    return True

def check_file_encoding():
    """Check file encodings that might cause issues."""
    files_to_check = [
        'nlp_pipeline\__init__.py',
        'nlp_pipeline\preprocessing\__init__.py', 
        'nlp_pipeline\preprocessing\cleaner.py'
    ]
    
    print("\n🔍 CHECKING FILE ENCODINGS")
    print("=" * 30)
    
    for file_path in files_to_check:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            try:
                # Read as bytes to check for null bytes
                with open(full_path, 'rb') as f:
                    content = f.read()
                    null_count = content.count(b'\x00')
                    
                print(f"📁 {file_path}:")
                print(f"   Size: {len(content)} bytes")
                print(f"   Null bytes: {null_count}")
                
                if null_count > 0:
                    print(f"   ❌ FOUND NULL BYTES!")
                    # Show where null bytes are
                    for i, byte in enumerate(content):
                        if byte == 0:
                            start = max(0, i-10)
                            end = min(len(content), i+10)
                            context = content[start:end]
                            print(f"   Null byte at position {i}: {context}")
                            break
                else:
                    print(f"   ✅ Clean")
                    
            except Exception as e:
                print(f"   ❌ Error reading {file_path}: {e}")
        else:
            print(f"📁 {file_path}: ❌ File not found")

if __name__ == "__main__":
    check_file_encoding()
    print("\n" + "="*50)
    success = test_import_step_by_step()
    
    if success:
        print("\n🎉 All imports successful!")
    else:
        print("\n💥 Import chain broken - see errors above")
    
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")