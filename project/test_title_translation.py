import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from issues.utils.translation_utils import get_short_korean_title, is_english_text

def test_title_translation():
    print("=== Testing Title Translation and Summarization ===")
    print()
    
    # Test cases with both Korean and English titles
    test_titles = [
        # English titles (should be translated to Korean)
        "Development and applicability evaluation of a nutrition education program for residents and users of disability social welfare facilities in Korea: a mixed-methods study",
        "Food and nutrient intake in pregnant women with singletons or multiples and post-delivery changes in intake in Korea: an observational study",
        "Nutritional content and healthiness in sweet and salty snacks and beverages popular in South Korea and the United States assessed by nutrition labels: a cross-sectional comparative study",
        
        # Korean titles (should be summarized directly)
        "장애인사회복지시설 입소•이용자를 대상으로 한 영양교육 프로그램 개발 및 적용성 평가",
        "근거 기반 나트륨 저감 건강 식생활 프로그램의 리빙랩 모델 적용",
        "한국 미취학 아동의 영양 수준과 주요 영향 요인: 1차 양육자의 식품 이해력, 사회적 지지, 그리고 식품 환경에 대한 단면 연구"
    ]
    
    for i, title in enumerate(test_titles, 1):
        print(f"Test {i}:")
        print(f"Original title: {title}")
        print(f"Is English: {is_english_text(title)}")
        print(f"Length: {len(title)} characters")
        
        # Get short Korean title
        short_title = get_short_korean_title(title, max_words=5)
        print(f"Short Korean title: {short_title}")
        print(f"Short title length: {len(short_title)} characters")
        print("-" * 80)
        print()

if __name__ == "__main__":
    test_title_translation() 