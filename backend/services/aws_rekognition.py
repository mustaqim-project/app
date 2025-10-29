"""
AWS Rekognition Service untuk Face Verification
Miluv.app
"""

import boto3
import os
import base64
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AWSRekognitionService:
    """Service untuk AWS Rekognition Face Comparison"""
    
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region = os.getenv('AWS_REGION', 'ap-southeast-1')
        self.collection_id = os.getenv('AWS_REKOGNITION_COLLECTION_ID', 'miluv-faces')
        
        # Initialize Rekognition client
        self.client = boto3.client(
            'rekognition',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region
        )
    
    def compare_faces(
        self, 
        source_image_base64: str, 
        target_image_base64: str,
        similarity_threshold: float = 90.0
    ) -> Dict[str, Any]:
        """
        Bandingkan 2 wajah menggunakan AWS Rekognition
        
        Args:
            source_image_base64: Base64 encoded foto profil
            target_image_base64: Base64 encoded selfie
            similarity_threshold: Threshold similarity (default 90%)
        
        Returns:
            {
                "is_match": bool,
                "similarity": float,
                "confidence": float
            }
        """
        try:
            # Decode base64 images
            source_bytes = self._decode_base64_image(source_image_base64)
            target_bytes = self._decode_base64_image(target_image_base64)
            
            # Call AWS Rekognition compare_faces
            response = self.client.compare_faces(
                SourceImage={'Bytes': source_bytes},
                TargetImage={'Bytes': target_bytes},
                SimilarityThreshold=similarity_threshold
            )
            
            # Check if faces match
            if response['FaceMatches']:
                match = response['FaceMatches'][0]
                similarity = match['Similarity']
                confidence = match['Face']['Confidence']
                
                return {
                    "is_match": True,
                    "similarity": round(similarity, 2),
                    "confidence": round(confidence, 2),
                    "face_detected": True
                }
            else:
                return {
                    "is_match": False,
                    "similarity": 0.0,
                    "confidence": 0.0,
                    "face_detected": len(response.get('UnmatchedFaces', [])) > 0,
                    "message": "Wajah tidak cocok atau tidak terdeteksi"
                }
                
        except self.client.exceptions.InvalidParameterException as e:
            return {
                "is_match": False,
                "similarity": 0.0,
                "confidence": 0.0,
                "face_detected": False,
                "error": "Format gambar tidak valid atau wajah tidak terdeteksi",
                "details": str(e)
            }
        except Exception as e:
            return {
                "is_match": False,
                "similarity": 0.0,
                "confidence": 0.0,
                "face_detected": False,
                "error": f"Error saat verifikasi wajah: {str(e)}"
            }
    
    def detect_faces(self, image_base64: str) -> Dict[str, Any]:
        """
        Deteksi wajah dalam gambar
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            {
                "faces_detected": int,
                "faces": [...],
                "has_face": bool
            }
        """
        try:
            image_bytes = self._decode_base64_image(image_base64)
            
            response = self.client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['DEFAULT']
            )
            
            faces = response.get('FaceDetails', [])
            
            return {
                "faces_detected": len(faces),
                "has_face": len(faces) > 0,
                "has_multiple_faces": len(faces) > 1,
                "faces": [
                    {
                        "confidence": face['Confidence'],
                        "age_range": face.get('AgeRange', {}),
                        "gender": face.get('Gender', {}),
                        "emotions": face.get('Emotions', [])
                    }
                    for face in faces
                ]
            }
            
        except Exception as e:
            return {
                "faces_detected": 0,
                "has_face": False,
                "error": str(e)
            }
    
    def _decode_base64_image(self, base64_string: str) -> bytes:
        """
        Decode base64 image string to bytes
        
        Args:
            base64_string: Base64 encoded image (with or without data:image prefix)
            
        Returns:
            bytes: Image bytes
        """
        # Remove data:image/xxx;base64, prefix if exists
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        return base64.b64decode(base64_string)
    
    def create_collection(self):
        """
        Buat collection untuk menyimpan wajah (opsional, untuk fitur advanced)
        """
        try:
            response = self.client.create_collection(
                CollectionId=self.collection_id
            )
            return {
                "success": True,
                "collection_arn": response['CollectionArn']
            }
        except self.client.exceptions.ResourceAlreadyExistsException:
            return {
                "success": True,
                "message": "Collection already exists"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
rekognition_service = AWSRekognitionService()


# Mock function for testing (gunakan ini jika belum punya AWS credentials)
def mock_compare_faces(source_base64: str, target_base64: str) -> Dict[str, Any]:
    """
    Mock function untuk testing tanpa AWS
    Selalu return True dengan similarity 95%
    """
    return {
        "is_match": True,
        "similarity": 95.0,
        "confidence": 98.5,
        "face_detected": True,
        "mock": True
    }
