import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from issues.utils.translation_utils import get_short_korean_title, is_english_text

def test_translation():
    print("=== Testing Translation Function ===")
    print()
    
    # Test cases
    test_titles = [
        "Development and applicability evaluation of a nutrition education program for residents and users of disability social welfare facilities in Korea: a mixed-methods study",
        "Food and nutrient intake in pregnant women with singletons or multiples and post-delivery changes in intake in Korea: an observational study",
        "장애인사회복지시설 입소•이용자를 대상으로 한 영양교육 프로그램 개발 및 적용성 평가",  # Already Korean
        "Nutritional content and healthiness in sweet and salty snacks and beverages popular in South Korea and the United States assessed by nutrition labels: a cross-sectional comparative study"
    ]
    
    for i, title in enumerate(test_titles, 1):
        print(f"Test {i}:")
        print(f"Original: {title}")
        print(f"Is English: {is_english_text(title)}")
        
        short_korean_title = get_short_korean_title(title, max_words=5)
        print(f"Short Korean: {short_korean_title}")
        print("-" * 80)
        print()

if __name__ == "__main__":
    test_translation() 