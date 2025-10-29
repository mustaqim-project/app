from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import math
import random
import base64
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'miluv_app')]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get('SECRET_KEY', 'miluv-secret-key-change-in-production-123456789')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# MODELS
# ============================================

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    date_of_birth: str
    gender: str  # male, female, other
    username: str
    profile_photo: str  # base64
    latitude: float
    longitude: float

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class FaceVerification(BaseModel):
    selfie_photo: str  # base64

class AssessmentAnswer(BaseModel):
    test_type: str  # mbti, love_language, readiness, temperament, disc
    answers: List[int]  # array of answer indices

class LikeUser(BaseModel):
    target_user_id: str

class SendMessage(BaseModel):
    match_id: str
    content: str
    message_type: str = "text"  # text, image, voice

class CreateFeed(BaseModel):
    content: str
    images: List[str] = []  # array of base64 images

class ReportItem(BaseModel):
    target_type: str  # user, feed
    target_id: str
    reason: str

class BookConsultation(BaseModel):
    counselor_id: str
    schedule: str
    session_type: str  # chat, video

# ============================================
# UTILS
# ============================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        user["id"] = str(user["_id"])
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km using Haversine formula"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def mock_face_verification(profile_photo: str, selfie_photo: str) -> bool:
    """Mock AWS Rekognition - always returns True for demo"""
    # In production, this would call AWS Rekognition API
    # For now, just return True
    return True

def calculate_compatibility_score(user1: dict, user2: dict) -> float:
    """Calculate compatibility based on assessment results"""
    score = 0.0
    
    # MBTI - 25%
    if user1.get('mbti') == user2.get('mbti'):
        score += 0.25
    elif user1.get('mbti') and user2.get('mbti'):
        # Similar type adds partial score
        if user1['mbti'][0] == user2['mbti'][0]:  # Same I/E
            score += 0.10
        if user1['mbti'][1] == user2['mbti'][1]:  # Same N/S
            score += 0.05
        if user1['mbti'][2] == user2['mbti'][2]:  # Same T/F
            score += 0.05
        if user1['mbti'][3] == user2['mbti'][3]:  # Same J/P
            score += 0.05
    
    # Love Language - 20%
    if user1.get('love_language') == user2.get('love_language'):
        score += 0.20
    elif user1.get('love_language') and user2.get('love_language'):
        score += 0.05  # Different but both have preference
    
    # Readiness - 30% (higher readiness = better match)
    if user1.get('readiness') and user2.get('readiness'):
        avg_readiness = (user1['readiness'] + user2['readiness']) / 2
        score += (avg_readiness / 100) * 0.30
    
    # Temperament - 15%
    if user1.get('temperament') == user2.get('temperament'):
        score += 0.15
    elif user1.get('temperament') and user2.get('temperament'):
        score += 0.05
    
    # DISC - 10%
    if user1.get('disc') == user2.get('disc'):
        score += 0.10
    elif user1.get('disc') and user2.get('disc'):
        score += 0.03
    
    return min(score * 100, 100)  # Convert to percentage

# ============================================
# ASSESSMENT QUESTIONS DATABASE
# ============================================

ASSESSMENT_QUESTIONS = {
    "mbti": [
        {"question": "Saya lebih suka berkumpul dengan banyak orang", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya lebih percaya pada intuisi daripada fakta", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya membuat keputusan berdasarkan logika", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka merencanakan segala sesuatu dengan detail", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya merasa energi setelah berinteraksi dengan orang", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya lebih fokus pada gambaran besar daripada detail", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya lebih mementingkan perasaan orang lain", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka spontanitas dan fleksibilitas", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya berbicara sebelum berpikir", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya lebih suka teori abstrak daripada praktikal", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]}
    ],
    "love_language": [
        {"question": "Saya merasa dicintai ketika pasangan memberikan hadiah", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Kata-kata pujian sangat berarti bagi saya", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya merasa dicintai saat pasangan meluangkan waktu bersama", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Sentuhan fisik membuat saya merasa terhubung", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Tindakan kecil seperti membantu pekerjaan sangat berarti", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Hadiah adalah simbol kasih sayang yang penting", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka mendengar kata-kata romantis dari pasangan", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Quality time bersama lebih penting dari hadiah mahal", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Pelukan dan ciuman sangat penting dalam hubungan", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya menghargai ketika pasangan membantu tanpa diminta", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]}
    ],
    "readiness": [
        {"question": "Saya siap berkomitmen dalam hubungan jangka panjang", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya sudah mengatasi trauma dari hubungan sebelumnya", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya tahu apa yang saya cari dalam pasangan", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya siap untuk berbagi hidup dengan orang lain", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya memiliki waktu untuk hubungan yang serius", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya siap untuk berkomunikasi secara terbuka", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya siap mengorbankan waktu pribadi untuk pasangan", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya percaya diri dengan diri saya sendiri", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya siap untuk membangun masa depan bersama", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya siap menghadapi konflik dengan matang", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]}
    ],
    "temperament": [
        {"question": "Saya adalah orang yang sangat sosial dan suka berbicara", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka mengambil kontrol dalam situasi", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya lebih suka menghindari konflik", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka menganalisis detail dan data", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya mudah bersemangat dan optimis", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka tantangan dan kompetisi", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya adalah pendengar yang baik dan sabar", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya perfeksionis dan detail-oriented", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya spontan dan ekspresif", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya tegas dalam mengambil keputusan", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]}
    ],
    "disc": [
        {"question": "Saya suka mengambil inisiatif dan memimpin", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka mempengaruhi dan membujuk orang lain", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya lebih suka stabilitas dan rutinitas", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya sangat teliti dan hati-hati", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya berorientasi pada hasil dan efisiensi", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya antusias dan senang bersosialisasi", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya loyal dan supportif terhadap tim", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka mengikuti aturan dan prosedur", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya berani mengambil risiko", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]},
        {"question": "Saya suka bekerja dengan orang lain", "options": ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]}
    ]
}

def calculate_assessment_result(test_type: str, answers: List[int]) -> dict:
    """Calculate assessment result based on answers"""
    
    if test_type == "mbti":
        # Simple MBTI calculation
        e_score = answers[0] + answers[4] + answers[8]
        n_score = answers[1] + answers[5] + answers[9]
        t_score = answers[2]
        j_score = answers[3]
        
        mbti = ""
        mbti += "E" if e_score >= 6 else "I"
        mbti += "N" if n_score >= 6 else "S"
        mbti += "T" if t_score >= 3 else "F"
        mbti += "J" if j_score >= 3 else "P"
        
        return {"type": mbti, "score": sum(answers) / len(answers) * 20}
    
    elif test_type == "love_language":
        # Calculate dominant love language
        gifts = (answers[0] + answers[5]) / 2
        words = (answers[1] + answers[6]) / 2
        quality_time = (answers[2] + answers[7]) / 2
        physical_touch = (answers[3] + answers[8]) / 2
        acts_of_service = (answers[4] + answers[9]) / 2
        
        scores = {
            "Gifts": gifts,
            "Words of Affirmation": words,
            "Quality Time": quality_time,
            "Physical Touch": physical_touch,
            "Acts of Service": acts_of_service
        }
        
        dominant = max(scores, key=scores.get)
        return {"type": dominant, "score": scores[dominant] * 20}
    
    elif test_type == "readiness":
        # Readiness percentage
        total = sum(answers)
        max_score = len(answers) * 4  # Max answer value is 4
        percentage = (total / max_score) * 100
        return {"type": "readiness", "score": percentage}
    
    elif test_type == "temperament":
        # Temperament types: Sanguine, Choleric, Phlegmatic, Melancholic
        sanguine = (answers[0] + answers[4] + answers[8]) / 3
        choleric = (answers[1] + answers[5] + answers[9]) / 3
        phlegmatic = (answers[2] + answers[6]) / 2
        melancholic = (answers[3] + answers[7]) / 2
        
        scores = {
            "Sanguine": sanguine,
            "Choleric": choleric,
            "Phlegmatic": phlegmatic,
            "Melancholic": melancholic
        }
        
        dominant = max(scores, key=scores.get)
        return {"type": dominant, "score": scores[dominant] * 20}
    
    elif test_type == "disc":
        # DISC types: Dominance, Influence, Steadiness, Compliance
        d_score = (answers[0] + answers[4] + answers[8]) / 3
        i_score = (answers[1] + answers[5] + answers[9]) / 3
        s_score = (answers[2] + answers[6]) / 2
        c_score = (answers[3] + answers[7]) / 2
        
        scores = {
            "Dominance": d_score,
            "Influence": i_score,
            "Steadiness": s_score,
            "Compliance": c_score
        }
        
        dominant = max(scores, key=scores.get)
        return {"type": dominant, "score": scores[dominant] * 20}
    
    return {"type": "unknown", "score": 0}

# ============================================
# ROUTES
# ============================================

@api_router.get("/")
async def root():
    return {"message": "Miluv.app API", "version": "1.0"}

# AUTH ENDPOINTS

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    """Register new user"""
    try:
        # Check if email already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if username already exists
        existing_username = await db.users.find_one({"username": user_data.username})
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Create user
        hashed_pw = hash_password(user_data.password)
        user_doc = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_pw,
            "date_of_birth": user_data.date_of_birth,
            "gender": user_data.gender,
            "username": user_data.username,
            "profile_photos": [user_data.profile_photo],
            "verified_face": False,
            "selfie_photo": None,
            "latitude": user_data.latitude,
            "longitude": user_data.longitude,
            "mbti": None,
            "love_language": None,
            "readiness": 0,
            "temperament": None,
            "disc": None,
            "assessments_completed": False,
            "role": "user",
            "created_at": datetime.utcnow(),
            "blocked_users": [],
            "bio": ""
        }
        
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Create token
        token = create_access_token({"sub": user_id})
        
        return {
            "message": "Registration successful",
            "token": token,
            "user_id": user_id,
            "needs_face_verification": True,
            "needs_assessment": True
        }
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    try:
        user = await db.users.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_id = str(user["_id"])
        token = create_access_token({"sub": user_id})
        
        return {
            "message": "Login successful",
            "token": token,
            "user_id": user_id,
            "verified_face": user.get("verified_face", False),
            "assessments_completed": user.get("assessments_completed", False),
            "readiness": user.get("readiness", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/verify-face")
async def verify_face(verification: FaceVerification, current_user: dict = Depends(get_current_user)):
    """Verify user face with selfie (mocked AWS Rekognition)"""
    try:
        profile_photo = current_user["profile_photos"][0]
        selfie_photo = verification.selfie_photo
        
        # Mock verification - in production, call AWS Rekognition
        is_match = mock_face_verification(profile_photo, selfie_photo)
        
        if is_match:
            await db.users.update_one(
                {"_id": ObjectId(current_user["id"])},
                {"$set": {"verified_face": True, "selfie_photo": selfie_photo}}
            )
            return {"message": "Face verified successfully", "verified": True}
        else:
            return {"message": "Face verification failed", "verified": False}
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ASSESSMENT ENDPOINTS

@api_router.get("/assessment/questions/{test_type}")
async def get_assessment_questions(test_type: str, current_user: dict = Depends(get_current_user)):
    """Get assessment questions"""
    if test_type not in ASSESSMENT_QUESTIONS:
        raise HTTPException(status_code=404, detail="Assessment type not found")
    
    return {
        "test_type": test_type,
        "questions": ASSESSMENT_QUESTIONS[test_type]
    }

@api_router.post("/assessment/submit")
async def submit_assessment(answer_data: AssessmentAnswer, current_user: dict = Depends(get_current_user)):
    """Submit assessment answers"""
    try:
        test_type = answer_data.test_type
        answers = answer_data.answers
        
        if test_type not in ASSESSMENT_QUESTIONS:
            raise HTTPException(status_code=404, detail="Assessment type not found")
        
        if len(answers) != 10:
            raise HTTPException(status_code=400, detail="Must provide 10 answers")
        
        # Calculate result
        result = calculate_assessment_result(test_type, answers)
        
        # Save to assessment_tests collection
        test_doc = {
            "user_id": current_user["id"],
            "test_type": test_type,
            "answers": answers,
            "result": result,
            "created_at": datetime.utcnow()
        }
        await db.assessment_tests.insert_one(test_doc)
        
        # Update user profile
        update_data = {}
        if test_type == "mbti":
            update_data["mbti"] = result["type"]
        elif test_type == "love_language":
            update_data["love_language"] = result["type"]
        elif test_type == "readiness":
            update_data["readiness"] = result["score"]
        elif test_type == "temperament":
            update_data["temperament"] = result["type"]
        elif test_type == "disc":
            update_data["disc"] = result["type"]
        
        await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": update_data}
        )
        
        # Check if all assessments completed
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        all_completed = all([
            user.get("mbti"),
            user.get("love_language"),
            user.get("readiness") is not None,
            user.get("temperament"),
            user.get("disc")
        ])
        
        if all_completed:
            await db.users.update_one(
                {"_id": ObjectId(current_user["id"])},
                {"$set": {"assessments_completed": True}}
            )
        
        return {
            "message": "Assessment submitted successfully",
            "result": result,
            "all_completed": all_completed
        }
    except Exception as e:
        logger.error(f"Assessment submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessment/status")
async def get_assessment_status(current_user: dict = Depends(get_current_user)):
    """Get user assessment completion status"""
    return {
        "mbti": current_user.get("mbti") is not None,
        "love_language": current_user.get("love_language") is not None,
        "readiness": current_user.get("readiness", 0),
        "temperament": current_user.get("temperament") is not None,
        "disc": current_user.get("disc") is not None,
        "all_completed": current_user.get("assessments_completed", False)
    }

# DISCOVER & MATCHING ENDPOINTS

@api_router.get("/discover")
async def discover_users(radius: int = 50, page: int = 1, limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Get discover list with matching algorithm"""
    try:
        # Check if assessments completed
        if not current_user.get("assessments_completed"):
            raise HTTPException(status_code=403, detail="Complete assessments first")
        
        # Get all users except current user
        users_cursor = db.users.find({
            "_id": {"$ne": ObjectId(current_user["id"])},
            "assessments_completed": True
        })
        
        users = await users_cursor.to_list(None)
        
        # Filter by radius and calculate compatibility
        candidates = []
        for user in users:
            # Skip blocked users
            if current_user["id"] in user.get("blocked_users", []):
                continue
            if str(user["_id"]) in current_user.get("blocked_users", []):
                continue
            
            # Calculate distance
            distance = calculate_distance(
                current_user["latitude"], 
                current_user["longitude"],
                user["latitude"], 
                user["longitude"]
            )
            
            if distance <= radius:
                # Calculate compatibility
                compatibility = calculate_compatibility_score(current_user, user)
                
                # Check if already liked or matched
                like_exists = await db.likes.find_one({
                    "from_user_id": current_user["id"],
                    "to_user_id": str(user["_id"])
                })
                
                candidates.append({
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "age": calculate_age(user["date_of_birth"]),
                    "gender": user["gender"],
                    "profile_photos": user["profile_photos"],
                    "bio": user.get("bio", ""),
                    "distance": round(distance, 1),
                    "compatibility": round(compatibility, 1),
                    "mbti": user.get("mbti"),
                    "love_language": user.get("love_language"),
                    "temperament": user.get("temperament"),
                    "disc": user.get("disc"),
                    "verified_face": user.get("verified_face", False),
                    "already_liked": like_exists is not None
                })
        
        # Sort by compatibility
        candidates.sort(key=lambda x: x["compatibility"], reverse=True)
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated = candidates[start:end]
        
        return {
            "users": paginated,
            "total": len(candidates),
            "page": page,
            "total_pages": math.ceil(len(candidates) / limit)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discover error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_age(date_of_birth: str) -> int:
    """Calculate age from date of birth"""
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except:
        return 0

@api_router.post("/like")
async def like_user(like_data: LikeUser, current_user: dict = Depends(get_current_user)):
    """Like a user (swipe right)"""
    try:
        target_user_id = like_data.target_user_id
        
        # Check if already liked
        existing_like = await db.likes.find_one({
            "from_user_id": current_user["id"],
            "to_user_id": target_user_id
        })
        
        if existing_like:
            return {"message": "Already liked", "match": False}
        
        # Create like
        like_doc = {
            "from_user_id": current_user["id"],
            "to_user_id": target_user_id,
            "created_at": datetime.utcnow()
        }
        await db.likes.insert_one(like_doc)
        
        # Check for mutual like
        reverse_like = await db.likes.find_one({
            "from_user_id": target_user_id,
            "to_user_id": current_user["id"]
        })
        
        if reverse_like:
            # Create match
            match_doc = {
                "user_a_id": current_user["id"],
                "user_b_id": target_user_id,
                "matched_at": datetime.utcnow()
            }
            match_result = await db.matches.insert_one(match_doc)
            match_id = str(match_result.inserted_id)
            
            # Create chat
            chat_doc = {
                "match_id": match_id,
                "user_a_id": current_user["id"],
                "user_b_id": target_user_id,
                "last_message": None,
                "updated_at": datetime.utcnow()
            }
            await db.chats.insert_one(chat_doc)
            
            return {
                "message": "It's a match!",
                "match": True,
                "match_id": match_id
            }
        
        return {"message": "Like sent", "match": False}
    except Exception as e:
        logger.error(f"Like error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/matches")
async def get_matches(current_user: dict = Depends(get_current_user)):
    """Get user matches"""
    try:
        # Find all matches involving current user
        matches_cursor = db.matches.find({
            "$or": [
                {"user_a_id": current_user["id"]},
                {"user_b_id": current_user["id"]}
            ]
        })
        
        matches = await matches_cursor.to_list(None)
        
        result = []
        for match in matches:
            # Get other user
            other_user_id = match["user_b_id"] if match["user_a_id"] == current_user["id"] else match["user_a_id"]
            other_user = await db.users.find_one({"_id": ObjectId(other_user_id)})
            
            if other_user:
                # Get last message
                chat = await db.chats.find_one({"match_id": str(match["_id"])})
                
                result.append({
                    "match_id": str(match["_id"]),
                    "user": {
                        "id": str(other_user["_id"]),
                        "name": other_user["name"],
                        "profile_photo": other_user["profile_photos"][0] if other_user["profile_photos"] else None
                    },
                    "last_message": chat.get("last_message") if chat else None,
                    "matched_at": match["matched_at"]
                })
        
        return {"matches": result}
    except Exception as e:
        logger.error(f"Get matches error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# CHAT ENDPOINTS

@api_router.get("/chat/{match_id}/messages")
async def get_messages(match_id: str, page: int = 1, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Get chat messages"""
    try:
        # Verify match exists and user is part of it
        match = await db.matches.find_one({"_id": ObjectId(match_id)})
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        if current_user["id"] not in [match["user_a_id"], match["user_b_id"]]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get messages
        messages_cursor = db.messages.find({"match_id": match_id}).sort("created_at", -1).skip((page - 1) * limit).limit(limit)
        messages = await messages_cursor.to_list(None)
        
        # Reverse to show oldest first
        messages.reverse()
        
        result = []
        for msg in messages:
            result.append({
                "id": str(msg["_id"]),
                "sender_id": msg["sender_id"],
                "content": msg["content"],
                "type": msg["type"],
                "created_at": msg["created_at"],
                "is_mine": msg["sender_id"] == current_user["id"]
            })
        
        return {"messages": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get messages error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/chat/{match_id}/messages")
async def send_message(match_id: str, message_data: SendMessage, current_user: dict = Depends(get_current_user)):
    """Send chat message"""
    try:
        # Verify match
        match = await db.matches.find_one({"_id": ObjectId(match_id)})
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        if current_user["id"] not in [match["user_a_id"], match["user_b_id"]]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Create message
        message_doc = {
            "match_id": match_id,
            "sender_id": current_user["id"],
            "content": message_data.content,
            "type": message_data.message_type,
            "created_at": datetime.utcnow()
        }
        result = await db.messages.insert_one(message_doc)
        
        # Update chat last_message
        await db.chats.update_one(
            {"match_id": match_id},
            {"$set": {"last_message": message_data.content, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message_id": str(result.inserted_id),
            "created_at": message_doc["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# FEEDS ENDPOINTS

@api_router.get("/feeds")
async def get_feeds(page: int = 1, limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Get feeds/timeline"""
    try:
        # Get feeds
        feeds_cursor = db.feeds.find({"visibility": "public"}).sort("created_at", -1).skip((page - 1) * limit).limit(limit)
        feeds = await feeds_cursor.to_list(None)
        
        # Get user's matches
        matches_cursor = db.matches.find({
            "$or": [
                {"user_a_id": current_user["id"]},
                {"user_b_id": current_user["id"]}
            ]
        })
        matches = await matches_cursor.to_list(None)
        matched_user_ids = set()
        for match in matches:
            other_id = match["user_b_id"] if match["user_a_id"] == current_user["id"] else match["user_a_id"]
            matched_user_ids.add(other_id)
        
        result = []
        for feed in feeds:
            user = await db.users.find_one({"_id": ObjectId(feed["user_id"])})
            
            # Show real name only if matched
            is_matched = feed["user_id"] in matched_user_ids
            display_name = user["name"] if is_matched else "Anonymous User"
            
            result.append({
                "id": str(feed["_id"]),
                "user": {
                    "id": feed["user_id"],
                    "name": display_name,
                    "profile_photo": user["profile_photos"][0] if is_matched and user["profile_photos"] else None
                },
                "content": feed["content"],
                "images": feed.get("images", []),
                "created_at": feed["created_at"],
                "is_mine": feed["user_id"] == current_user["id"]
            })
        
        return {"feeds": result}
    except Exception as e:
        logger.error(f"Get feeds error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/feeds")
async def create_feed(feed_data: CreateFeed, current_user: dict = Depends(get_current_user)):
    """Create new feed post"""
    try:
        feed_doc = {
            "user_id": current_user["id"],
            "content": feed_data.content,
            "images": feed_data.images,
            "visibility": "public",
            "created_at": datetime.utcnow()
        }
        result = await db.feeds.insert_one(feed_doc)
        
        return {
            "feed_id": str(result.inserted_id),
            "message": "Feed created successfully"
        }
    except Exception as e:
        logger.error(f"Create feed error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# PROFILE ENDPOINTS

@api_router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "username": current_user["username"],
        "age": calculate_age(current_user["date_of_birth"]),
        "gender": current_user["gender"],
        "profile_photos": current_user["profile_photos"],
        "bio": current_user.get("bio", ""),
        "verified_face": current_user.get("verified_face", False),
        "mbti": current_user.get("mbti"),
        "love_language": current_user.get("love_language"),
        "readiness": current_user.get("readiness", 0),
        "temperament": current_user.get("temperament"),
        "disc": current_user.get("disc"),
        "assessments_completed": current_user.get("assessments_completed", False)
    }

@api_router.get("/profile/{user_id}")
async def get_user_profile(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get other user profile"""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "username": user["username"],
            "age": calculate_age(user["date_of_birth"]),
            "gender": user["gender"],
            "profile_photos": user["profile_photos"],
            "bio": user.get("bio", ""),
            "verified_face": user.get("verified_face", False),
            "mbti": user.get("mbti"),
            "love_language": user.get("love_language"),
            "temperament": user.get("temperament"),
            "disc": user.get("disc")
        }
    except Exception as e:
        logger.error(f"Get user profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# REPORT & BLOCK

@api_router.post("/report")
async def report_item(report_data: ReportItem, current_user: dict = Depends(get_current_user)):
    """Report user or feed"""
    try:
        report_doc = {
            "reporter_id": current_user["id"],
            "target_type": report_data.target_type,
            "target_id": report_data.target_id,
            "reason": report_data.reason,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        await db.reports.insert_one(report_doc)
        
        return {"message": "Report submitted successfully"}
    except Exception as e:
        logger.error(f"Report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/block/{user_id}")
async def block_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Block user"""
    try:
        # Add to blocked list
        await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$addToSet": {"blocked_users": user_id}}
        )
        
        return {"message": "User blocked successfully"}
    except Exception as e:
        logger.error(f"Block error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# CONSULTATION ENDPOINTS (Mocked)

@api_router.get("/consultations")
async def get_consultations(current_user: dict = Depends(get_current_user)):
    """Get available counselors (only if readiness >= 80%)"""
    try:
        if current_user.get("readiness", 0) < 80:
            raise HTTPException(
                status_code=403, 
                detail="Consultation requires readiness score of 80% or higher. Please retake assessments."
            )
        
        # Mock counselors data
        counselors = [
            {
                "id": "counselor-1",
                "name": "Dr. Sarah Johnson",
                "specialization": "Relationship Counseling",
                "price": 150000,
                "rating": 4.8
            },
            {
                "id": "counselor-2",
                "name": "Dr. Michael Chen",
                "specialization": "Marriage Therapy",
                "price": 200000,
                "rating": 4.9
            }
        ]
        
        return {"counselors": counselors}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get consultations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/consultations/book")
async def book_consultation(booking: BookConsultation, current_user: dict = Depends(get_current_user)):
    """Book consultation (mocked payment)"""
    try:
        if current_user.get("readiness", 0) < 80:
            raise HTTPException(status_code=403, detail="Consultation requires readiness >= 80%")
        
        # Mock Xendit payment
        payment_id = f"payment-{uuid.uuid4()}"
        
        consult_doc = {
            "user_id": current_user["id"],
            "counselor_id": booking.counselor_id,
            "schedule": booking.schedule,
            "session_type": booking.session_type,
            "payment_id": payment_id,
            "status": "confirmed",
            "created_at": datetime.utcnow()
        }
        result = await db.consults.insert_one(consult_doc)
        
        return {
            "message": "Consultation booked successfully",
            "consult_id": str(result.inserted_id),
            "payment_id": payment_id,
            "status": "confirmed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book consultation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
