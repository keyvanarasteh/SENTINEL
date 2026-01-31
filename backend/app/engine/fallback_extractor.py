"""
Fallback extraction for unsupported languages using regex patterns.
"""
import re
from typing import List, Dict

class FallbackExtractor:
    """Extract code blocks from unsupported languages using regex."""
    
    # Common patterns across many languages
    FUNCTION_PATTERNS = [
        r'(?:function|def|fn|func|fun|func)\s+(\w+)\s*\([^)]*\)\s*(?:{|:)',  # Functions
        r'(?:class|struct|type|interface)\s+(\w+)',  # Classes/Types
        r'(?:const|let|var|val)\s+(\w+)\s*=',  # Variables
    ]
    
    def extract(self, content: str, filename: str) -> List[Dict]:
        """
        Extract code blocks using regex patterns.
        
        Returns list of blocks with lower confidence.
        """
        blocks = []
        lines = content.split('\n')
        
        # Split by empty lines for basic segmentation
        current_block = []
        for i, line in enumerate(lines):
            if line.strip():
                current_block.append(line)
            elif current_block:
                # End of block
                blocks.append({
                    'content': '\n'.join(current_block),
                    'start_line': i - len(current_block) + 1,
                    'end_line': i,
                    'confidence': 0.6,  # Lower confidence for fallback
                    'extraction_method': 'fallback_regex',
                    'language': 'unknown' # Will be filled by caller
                })
                current_block = []
        
        # Last block
        if current_block:
            blocks.append({
                'content': '\n'.join(current_block),
                'start_line': len(lines) - len(current_block) + 1,
                'end_line': len(lines),
                'confidence': 0.6,
                'extraction_method': 'fallback_regex',
                'language': 'unknown'
            })
        
        return blocks
