from fastapi import APIRouter, UploadFile, File
import base64, os, openai
from PIL import Image
import io
from dotenv import load_dotenv

router = APIRouter()

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def encode_image(file: UploadFile):
    content = file.file.read()
    return base64.b64encode(content).decode("utf-8")

@router.post("/analyze")
async def analyze_food(file: UploadFile = File(...)):
    encoded = encode_image(file)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
You are a food image analysis expert with deep knowledge in culinary arts. 
If there are more than two food photos, please add the two values together. 
Please analyze the food image provided below carefully, considering its appearance, ingredients, and regional characteristics.  
Provide the following information:

- Dish name
- exact calories (in kcal)
- carbohydrates in the food(grams)
- protein in the food(grams)
- fat in the food(grams)
- Sodium in this food(grams)
- Dietary fiber in that food(grams)
- Number of foods and total amount (grams)

⚠ IMPORTANT: Your response must be written in Korean at the end

Format your response exactly like this:

- 요리명: (dish name in Korean)
- 칼로리: (exact calories in kcal)
- 탄수화물: (carbohydrates in the food(grams))
- 단백질: (protein in the food(grams))
- 지방: (fat in the food(grams))
- 나트륨: (Sodium in this food(grams))
- 식이섬유: (Dietary fiber in that food(grams))
- 총량: (Number of foods and total amount (grams))
"""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded}"
                    }
                }
            ]
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=300
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}

@router.get("/")
def meals_root():
    return {"status": "Meals API is running"} 