import re
from typing import List, Dict, Optional

class SecretScanner:
    """
    Kod blokları içindeki hassas verileri (API Key, Password, Token) tespit eder.
    Regex tabanlı tarama yapar.
    """
    
    # Yaygın Hassas Veri Desenleri
    PATTERNS = {
        'AWS_ACCESS_KEY': r'\bAKIA[0-9A-Z]{16}\b',
        'AWS_SECRET_KEY': r'\b[0-9a-zA-Z/+]{40}\b',
        'GOOGLE_API_KEY': r'\bAIza[0-9A-Za-z\\-_]{35}\b',
        'SLACK_TOKEN': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
        'PRIVATE_KEY': r'-----BEGIN\s+([A-Z\s]+)\s+PRIVATE\s+KEY-----',
        'GENERIC_PASSWORD': r'(?i)(password|passwd|pwd|secret|auth_token|api_key|bearer)\s*[:=]\s*["\']([^"\']{6,})["\']',
        'DB_CONNECTION': r'(?i)(mysql|postgres|mongodb|redis).*?://.*?:(.*?)@',
        'STRIPE_KEY': r'\bsk_live_[0-9a-zA-Z]{24}\b',
        'GITHUB_TOKEN': r'\bgh[pousr]_[a-zA-Z0-9]{36}\b'
    }

    @classmethod
    def has_secrets(cls, content: str) -> bool:
        """Bir içerikte herhangi bir sır olup olmadığını hızlıca kontrol eder."""
        if not content or len(content) > 100000: # Çok büyük dosyaları atla veya limit koy
            return False
            
        for pattern in cls.PATTERNS.values():
            if re.search(pattern, content):
                return True
        return False

    @classmethod
    def get_secret_types(cls, content: str) -> List[str]:
        """İçerikte bulunan sırların tiplerini döndürür (Örn: ['AWS_ACCESS_KEY'])."""
        found_types = []
        for name, pattern in cls.PATTERNS.items():
            if re.search(pattern, content):
                found_types.append(name)
        return list(set(found_types))

    @classmethod
    def scan(cls, content: str) -> List[Dict]:
        """Detaylı tarama raporu döndürür."""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for name, pattern in cls.PATTERNS.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    findings.append({
                        'type': name,
                        'line': i + 1,
                        'match_start': match.start(),
                        'match_end': match.end(),
                        # Güvenlik gereği tam değeri loglamıyoruz, sadece varlığını bildiriyoruz
                        'snippet': line.strip()[:50] + "..." 
                    })
        return findings