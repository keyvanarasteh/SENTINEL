"""
Batch Processing Engine
Handles parallel processing of multiple files with progress tracking
"""
import asyncio
from typing import List, Dict
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.models import FileMetadata, ExtractedBlock
from app.engine.normalizer import FileNormalizer
from app.engine.segmenter import Segmenter
from app.engine.validator import Validator
from app.engine.filter import PrecisionFilter


class BatchProcessor:
    """Process multiple files in parallel with progress tracking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.normalizer = FileNormalizer()
        self.segmenter = Segmenter()
        self.validator = Validator()
        self.filter = PrecisionFilter()
        
        # Track batch progress
        self.batch_status: Dict[str, Dict] = {}
    
    async def process_batch(
        self,
        batch_id: str,
        file_ids: List[int],
        session_id: int = None
    ) -> Dict:
        """
        Process multiple files in parallel
        
        Args:
            batch_id: Unique batch identifier
            file_ids: List of file IDs to process
            session_id: Optional session to link extracted blocks
            
        Returns:
            Batch processing summary
        """
        # Initialize batch status
        self.batch_status[batch_id] = {
            "total_files": len(file_ids),
            "completed_files": 0,
            "failed_files": 0,
            "in_progress": True,
            "start_time": datetime.utcnow(),
            "file_statuses": {}
        }
        
        # Process files concurrently
        tasks = [
            self._process_single_file(batch_id, file_id, session_id)
            for file_id in file_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update final status
        self.batch_status[batch_id]["in_progress"] = False
        self.batch_status[batch_id]["end_time"] = datetime.utcnow()
        
        return self.batch_status[batch_id]
    
    async def _process_single_file(
        self,
        batch_id: str,
        file_id: int,
        session_id: int = None
    ) -> Dict:
        """Process a single file within a batch"""
        try:
            # Update file status
            self.batch_status[batch_id]["file_statuses"][file_id] = {
                "status": "processing",
                "start_time": datetime.utcnow(),
                "blocks_extracted": 0,
                "error": None
            }
            
            # Get file from database
            file = self.db.query(FileMetadata).filter(
                FileMetadata.id == file_id
            ).first()
            
            if not file:
                raise Exception(f"File {file_id} not found")
            
            # Update file status in database
            file.processing_status = "processing"
            self.db.commit()
            
            # Determine file path
            # If original_path is absolute and exists (e.g. from Git clone), use it
            # Otherwise fall back to uploads directory
            import os
            if file.original_path and os.path.isabs(file.original_path) and os.path.exists(file.original_path):
                file_path = file.original_path
            else:
                file_path = f"data/uploads/{file.filename}"
            
            # Normalize based on file type
            if file.file_type == "pdf":
                normalized_text = await asyncio.to_thread(
                    self.normalizer.normalize_pdf, file_path
                )
            elif file.file_type == "docx":
                normalized_text = await asyncio.to_thread(
                    self.normalizer.normalize_docx, file_path
                )
            else:  # txt or other text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                normalized_text = self.normalizer._normalize_text(content)
            
            # Segment text
            segments = await asyncio.to_thread(
                self.segmenter.segment, normalized_text
            )
            
            # Validate and filter blocks
            extracted_blocks = []
            for segment in segments:
                # Validate
                result = self.validator.validate_block(segment['content'])
                
                if result['is_valid']:
                    # Filter
                    filter_result = self.filter.filter_block(
                        content=segment['content'],
                        language=result.get('language'),
                        confidence=result.get('confidence', 0)
                    )
                    
                    if filter_result['should_keep']:
                        # Save block
                        block = ExtractedBlock(
                            file_id=file_id,
                            session_id=session_id,
                            content=segment['content'],
                            language=result.get('language'),
                            block_type=result.get('type', 'code'),
                            confidence_score=filter_result.get(
                                'adjusted_confidence',
                                result.get('confidence', 0)
                            ),
                            validation_method=result.get('method', 'unknown'),
                            start_line=segment.get('start_line'),
                            end_line=segment.get('end_line')
                        )
                        self.db.add(block)
                        extracted_blocks.append(block)
            
            # Commit all blocks
            self.db.commit()
            
            # Update file status
            file.processing_status = "complete"
            self.db.commit()
            
            # Update batch progress
            self.batch_status[batch_id]["completed_files"] += 1
            self.batch_status[batch_id]["file_statuses"][file_id].update({
                "status": "complete",
                "end_time": datetime.utcnow(),
                "blocks_extracted": len(extracted_blocks),
                "error": None
            })
            
            return {
                "file_id": file_id,
                "status": "success",
                "blocks_count": len(extracted_blocks)
            }
            
        except Exception as e:
            # Handle error
            self.batch_status[batch_id]["failed_files"] += 1
            self.batch_status[batch_id]["file_statuses"][file_id].update({
                "status": "error",
                "end_time": datetime.utcnow(),
                "error": str(e)
            })
            
            # Update file in database
            if file:
                file.processing_status = "error"
                self.db.commit()
            
            return {
                "file_id": file_id,
                "status": "error",
                "error": str(e)
            }
    
    def get_batch_status(self, batch_id: str) -> Dict:
        """Get current status of a batch"""
        return self.batch_status.get(batch_id, None)
