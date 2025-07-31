import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from issues.utils.translation_utils import get_short_korean_title, summarize_title

def test_korean_title():
    print("=== Testing Korean Title Summarization ===")
    print()
    
    # The Korean title you provided
    korean_title = "한국 미취학 아동의 영양 수준과 주요 영향 요인: 1차 양육자의 식품 이해력, 사회적 지지, 그리고 식품 환경에 대한 단면 연구"
    
    print(f"Original Korean title: {korean_title}")
    print(f"Length: {len(korean_title)} characters")
    print()
    
    # Test short title summarization
    short_title = get_short_korean_title(korean_title, max_words=5)
    print(f"Short Korean title: {short_title}")
    print(f"Length: {len(short_title)} characters")
    print()
    
    # Test direct summarization
    direct_summary = summarize_title(korean_title, max_words=5)
    print(f"Direct summary: {direct_summary}")
    print(f"Length: {len(direct_summary)} characters")

if __name__ == "__main__":
    test_korean_title() 