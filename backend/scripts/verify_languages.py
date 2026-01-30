
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.engine.validator import Validator
from app.engine.segmenter import CandidateBlock

def test_language(name, code, expected_lang):
    print(f"Testing {name}...")
    validator = Validator()
    
    # Mock candidate block
    block = CandidateBlock(
        content=code,
        start_line=1,
        end_line=10,
        detection_method="manual",
        language_hint=None,
        confidence=1.0
    )
    
    result = validator.validate_block(block)
    
    if result['valid'] and result['language'] == expected_lang:
        print(f"  ✅ Detected {expected_lang} with confidence {result['confidence_score']:.2f}")
    else:
        print(f"  ❌ Failed to detect {expected_lang}. Result: {result}")

if __name__ == "__main__":
    # Python (Control)
    test_language("Python", "def hello(): pass", "python")
    
    # Ruby
    test_language("Ruby", "def hello; puts 'world'; end", "ruby")
    
    # PHP
    test_language("PHP", "<?php echo 'Hello'; ?>", "php")
    
    # C#
    test_language("C#", "public class Program { public static void Main() {} }", "c_sharp")
    
    # Bash
    test_language("Bash", "#!/bin/bash\necho 'Hello'", "bash")
    
    # Swift
    test_language("Swift", "func hello() { print(\"Hello\") }", "swift")
