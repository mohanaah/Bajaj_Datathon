"""
Document processing utilities for downloading and converting documents
"""
import requests
import io
import os
import shutil
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
from typing import List, Tuple
from utils.logger import logger
import config

class DocumentProcessor:
    """Process documents from URLs - download, OCR, and extract text"""
    
    def __init__(self):
        self.tesseract_cmd = self._find_tesseract()
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            # Verify Tesseract is accessible
            try:
                pytesseract.get_tesseract_version()
                logger.info(f"Tesseract found at: {self.tesseract_cmd}")
            except Exception as e:
                logger.error(f"Tesseract found but not accessible: {str(e)}")
                raise RuntimeError(f"Tesseract is not accessible at {self.tesseract_cmd}. Please install Tesseract OCR.")
        else:
            raise RuntimeError(
                "Tesseract OCR is not installed or not found in PATH. "
                "Please install it:\n"
                "  macOS: brew install tesseract\n"
                "  Ubuntu: sudo apt-get install tesseract-ocr\n"
                "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
    def _find_tesseract(self) -> str:
        """Find Tesseract installation path"""
        # First check config
        if config.TESSERACT_CMD and os.path.exists(config.TESSERACT_CMD):
            return config.TESSERACT_CMD
        
        # Check common installation paths
        common_paths = [
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",  # Apple Silicon Mac
            "/usr/bin/tesseract",
            shutil.which("tesseract"),  # Check PATH
        ]
        
        for path in common_paths:
            if path and os.path.exists(path):
                return path
        
        return None
    
    def download_document(self, url: str) -> bytes:
        """Download document from URL"""
        try:
            logger.info(f"Downloading document from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            logger.info(f"Successfully downloaded document, size: {len(response.content)} bytes")
            return response.content
        except Exception as e:
            logger.error(f"Error downloading document: {str(e)}")
            raise
    
    def is_pdf(self, content: bytes) -> bool:
        """Check if content is a PDF"""
        return content[:4] == b'%PDF'
    
    def is_image(self, content: bytes) -> bool:
        """Check if content is an image"""
        try:
            Image.open(io.BytesIO(content))
            return True
        except:
            return False
    
    def pdf_to_images(self, pdf_content: bytes) -> List[Image.Image]:
        """Convert PDF to list of PIL Images"""
        try:
            logger.info("Converting PDF to images")
            images = convert_from_bytes(pdf_content, dpi=300)
            logger.info(f"Converted PDF to {len(images)} pages")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise
    
    def image_to_text(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""
        try:
            text = pytesseract.image_to_string(image, lang='eng')
            return text
        except Exception as e:
            logger.error(f"Error in OCR: {str(e)}")
            raise
    
    def process_document(self, url: str) -> List[Tuple[int, str]]:
        """
        Process document from URL and return list of (page_number, text) tuples
        Returns: List of (page_no, text) tuples
        """
        content = self.download_document(url)
        pages = []
        
        if self.is_pdf(content):
            images = self.pdf_to_images(content)
            for idx, image in enumerate(images, start=1):
                logger.info(f"Processing page {idx} of PDF")
                text = self.image_to_text(image)
                pages.append((idx, text))
        elif self.is_image(content):
            logger.info("Processing single image document")
            image = Image.open(io.BytesIO(content))
            text = self.image_to_text(image)
            pages.append((1, text))
        else:
            raise ValueError("Unsupported document format")
        
        return pages


