from fastapi import FastAPI, Header, UploadFile, File
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
import base64
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings  
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
import openai
import pandas as pd
from pathlib import Path
from typing import List, Optional

# Import routers
from issues.routes import router as issues_router
from meals.routes import router as meals_router

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Haru Python API", version="1.0.0")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(issues_router, prefix="/issues", tags=["issues"])
app.include_router(meals_router, prefix="/meals", tags=["meals"])

class Question(BaseModel):
    question: str
    user_id: Optional[str] = None

knowledge_base = None

@app.on_event("startup")
def startup_event():
    global knowledge_base
    print("🚀 지식베이스 초기화 시작...")
    data_dir = Path(__file__).parent.parent / "data"
    files = list(data_dir.glob("*.*"))
    knowledge_base = init_knowledge_base(files)
    print("✅ 지식베이스 초기화 완료!")

def process_large_food_csv(file_path: Path, chunk_size: int = 1000) -> List[str]:
    """대용량 음식 CSV 파일을 청크 단위로 처리"""
    chunks = []
    
    try:
        print(f"대용량 파일 처리 시작: {file_path.name}")
        
        encodings_to_try = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
        chunk_iter = None
        
        for encoding in encodings_to_try:
            try:
                chunk_iter = pd.read_csv(file_path, chunksize=chunk_size, encoding=encoding)
                print(f"  성공한 인코딩: {encoding}")
                break
            except UnicodeDecodeError:
                print(f"  실패한 인코딩: {encoding}")
                continue
        
        if chunk_iter is None:
            print(f"  모든 인코딩 실패: {file_path.name}")
            return []
        
        for i, chunk_df in enumerate(chunk_iter):
            processed_texts = []
            
            for _, row in chunk_df.iterrows():
                try:
                    row_text = convert_nutrition_row_to_text(row, chunk_df.columns)
                    if row_text:
                        processed_texts.append(row_text)
                except Exception as e:
                    continue
            
            if processed_texts:
                chunk_text = f"=== {file_path.name} 청크 {i+1} ===\n" + "\n".join(processed_texts)
                chunks.append(chunk_text)
        
        print(f"  처리 완료: {len(chunks)}개 청크 생성")
        return chunks
        
    except Exception as e:
        print(f"  파일 처리 오류: {e}")
        return []

def convert_nutrition_row_to_text(row, columns) -> str:
    """영양 정보 행을 자연어 텍스트로 변환"""
    try:
        # 기본 정보 추출
        food_name = row.get('음식명', row.get('name', 'Unknown'))
        
        # 영양소 정보 구성
        nutrition_info = []
        
        # 주요 영양소들
        nutrition_mapping = {
            '칼로리': ['칼로리', 'calories', 'kcal'],
            '탄수화물': ['탄수화물', 'carbohydrates', 'carbs'],
            '단백질': ['단백질', 'protein'],
            '지방': ['지방', 'fat'],
            '나트륨': ['나트륨', 'sodium'],
            '식이섬유': ['식이섬유', 'fiber', 'dietary_fiber']
        }
        
        for nutrient_name, possible_keys in nutrition_mapping.items():
            for key in possible_keys:
                if key in columns and pd.notna(row[key]):
                    value = row[key]
                    nutrition_info.append(f"{nutrient_name}: {value}")
                    break
        
        if nutrition_info:
            return f"{food_name} - {' | '.join(nutrition_info)}"
        else:
            return f"{food_name}"
            
    except Exception as e:
        return ""

def init_knowledge_base(file_paths: List[Path]):
    """지식베이스 초기화"""
    try:
        all_texts = []
        
        for file_path in file_paths:
            if file_path.suffix.lower() == '.csv':
                # CSV 파일 처리
                csv_texts = process_large_food_csv(file_path)
                all_texts.extend(csv_texts)
            else:
                # 기타 파일 처리 (기존 로직)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        all_texts.append(text)
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='cp949') as f:
                            text = f.read()
                            all_texts.append(text)
                    except:
                        print(f"파일 읽기 실패: {file_path}")
                        continue
        
        if not all_texts:
            print("⚠️ 처리할 텍스트가 없습니다.")
            return None
        
        # 텍스트 분할
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.split_text("\n".join(all_texts))
        
        # 임베딩 생성
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        
        print(f"✅ 지식베이스 생성 완료: {len(chunks)}개 청크")
        return knowledge_base
        
    except Exception as e:
        print(f"❌ 지식베이스 초기화 실패: {e}")
        return None

def detect_command(question: str) -> tuple[bool, str]:
    """명령어 감지"""
    commands = {
        "crawl": ["크롤링", "crawl", "웹페이지", "기사"],
        "food_analyze": ["음식 분석", "food", "analyze", "이미지"]
    }
    
    question_lower = question.lower()
    
    for command, keywords in commands.items():
        if any(keyword in question_lower for keyword in keywords):
            return True, command
    
    return False, ""

def detect_food_question(question: str) -> bool:
    """음식 관련 질문 감지"""
    food_keywords = [
        "음식", "식사", "밥", "아침", "점심", "저녁", "간식",
        "칼로리", "영양", "다이어트", "운동", "식단",
        "food", "meal", "breakfast", "lunch", "dinner", "snack",
        "calorie", "nutrition", "diet", "exercise"
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in food_keywords)

async def call_external_api(command_type: str, user_id: str = None) -> dict:
    """외부 API 호출"""
    try:
        if command_type == "crawl":
            # 크롤링 API 호출 로직
            return {"message": "크롤링 기능은 /issues/crawl 엔드포인트를 사용하세요"}
        elif command_type == "food_analyze":
            # 음식 분석 API 호출 로직
            return {"message": "음식 분석 기능은 /meals/analyze 엔드포인트를 사용하세요"}
        else:
            return {"error": "알 수 없는 명령어"}
    except Exception as e:
        return {"error": str(e)}

async def get_user_profile(user_id: str = None) -> dict:
    """사용자 프로필 조회"""
    # 기본 프로필 (실제로는 데이터베이스에서 조회)
    base_profile = {
        "weight": 60,
        "height": 170,
        "age": 25,
        "activity_level": "moderate",
        "goal": "maintain"
    }
    
    if user_id:
        # TODO: 실제 사용자 데이터 조회 로직
        pass
    
    return base_profile

def extract_user_info(question: str, base_profile: dict) -> dict:
    """질문에서 사용자 정보 추출"""
    user_info = base_profile.copy()
    
    # 키워드 기반 정보 추출
    question_lower = question.lower()
    
    # 체중 정보 추출
    if "몸무게" in question_lower or "체중" in question_lower:
        # 간단한 키워드 매칭 (실제로는 더 정교한 NLP 필요)
        pass
    
    return user_info

def calculate_exercise_time(target_calories: int, weight_kg: int = 60) -> str:
    """운동 시간 계산"""
    # 기본 칼로리 소모량 (MET 기준)
    activities = {
        "걷기": 3.5,
        "조깅": 7.0,
        "달리기": 10.0,
        "자전거": 6.0,
        "수영": 8.0
    }
    
    results = []
    
    for activity, met in activities.items():
        # 칼로리 소모량 = MET × 체중(kg) × 시간(시간)
        # 시간 = 목표 칼로리 ÷ (MET × 체중)
        hours = target_calories / (met * weight_kg)
        minutes = int(hours * 60)
        
        if minutes < 60:
            results.append(f"{activity}: {minutes}분")
        else:
            hours_int = minutes // 60
            mins_remain = minutes % 60
            results.append(f"{activity}: {hours_int}시간 {mins_remain}분")
    
    return " | ".join(results)

@app.post("/ask")
async def ask_question(request: Question):
    """메인 질문-답변 엔드포인트"""
    try:
        question = request.question
        user_id = request.user_id
        
        # 명령어 감지
        is_command, command_type = detect_command(question)
        if is_command:
            result = await call_external_api(command_type, user_id)
            return {"type": "command", "result": result}
        
        # 음식 관련 질문인지 확인
        if detect_food_question(question):
            if knowledge_base:
                # 지식베이스 검색
                docs = knowledge_base.similarity_search(question, k=3)
                
                # LLM을 사용한 답변 생성
                llm = ChatOpenAI(temperature=0.3)
                chain = load_qa_chain(llm, chain_type="stuff")
                
                result = chain.run(input_documents=docs, question=question)
                
                # 사용자 프로필 기반 개인화
                user_profile = await get_user_profile(user_id)
                user_info = extract_user_info(question, user_profile)
                
                # 운동 시간 계산 (칼로리 관련 질문인 경우)
                if "칼로리" in question.lower() or "운동" in question.lower():
                    # 간단한 칼로리 추출 (실제로는 더 정교한 NLP 필요)
                    exercise_info = calculate_exercise_time(300, user_info["weight"])
                    result += f"\n\n💪 운동 추천: {exercise_info}"
                
                return {
                    "type": "food_question",
                    "answer": result,
                    "user_profile": user_info
                }
            else:
                return {
                    "type": "error",
                    "message": "지식베이스가 초기화되지 않았습니다."
                }
        else:
            # 일반적인 질문에 대한 기본 답변
            return {
                "type": "general",
                "message": "음식이나 영양에 관한 질문을 해주세요. 크롤링이나 음식 분석 기능도 사용할 수 있습니다."
            }
            
    except Exception as e:
        return {"type": "error", "message": str(e)}

@app.get("/commands")
async def get_available_commands():
    """사용 가능한 명령어 목록"""
    return {
        "commands": [
            {
                "name": "crawl",
                "description": "웹페이지 크롤링",
                "endpoint": "/issues/crawl",
                "keywords": ["크롤링", "crawl", "웹페이지", "기사"]
            },
            {
                "name": "food_analyze",
                "description": "음식 이미지 분석",
                "endpoint": "/meals/analyze",
                "keywords": ["음식 분석", "food", "analyze", "이미지"]
            }
        ]
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "knowledge_base": knowledge_base is not None}

@app.get("/")
def root():
    return {
        "message": "Haru Python API",
        "version": "1.0.0",
        "endpoints": {
            "main": "/ask",
            "issues": "/issues",
            "meals": "/meals",
            "health": "/health",
            "commands": "/commands"
        }
    }

    
