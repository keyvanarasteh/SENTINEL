"""
Export Service - Logic for handling various export formats (ZIP, JSONL, Parquet)
"""
import zipfile
import json
import io
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models import ExtractedBlock, FileMetadata

class ExportService:
    def __init__(self, export_dir: Path):
        self.export_dir = export_dir

    def _get_extension(self, language: str) -> str:
        """Get file extension for language."""
        ext_map = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'c': '.c',
            'cpp': '.cpp',
            'go': '.go',
            'rust': '.rs',
            'json': '.json',
            'yaml': '.yaml',
            'xml': '.xml',
        }
        return ext_map.get(language, '.txt')

    def _get_config_extension(self, config_type: str) -> str:
        """Get extension for config files."""
        ext_map = {
            'cisco_ios': '.cfg',
            'nginx': '.conf',
            'json': '.json',
            'yaml': '.yaml',
            'xml': '.xml',
        }
        return ext_map.get(config_type, '.conf')

    def generate_zip(self, file_meta: FileMetadata, blocks: List[ExtractedBlock]) -> Path:
        """Generate a ZIP export."""
        zip_filename = f"hpes_export_{file_meta.id}_{file_meta.file_hash[:8]}.zip"
        zip_path = self.export_dir / zip_filename
        
        categories = {}
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add blocks organized by category
            for idx, block in enumerate(blocks):
                # Determine folder based on block type and language
                if block.block_type == 'code':
                    folder = f"{block.language}_codes"
                    ext = self._get_extension(block.language)
                    filename = f"block_{idx+1:03d}{ext}"
                elif block.block_type == 'config':
                    folder = "configs"
                    ext = self._get_config_extension(block.language)
                    filename = f"{block.language}_{idx+1:03d}{ext}"
                elif block.block_type == 'log':
                    folder = "logs"
                    filename = f"log_{idx+1:03d}.log"
                elif block.block_type == 'structured':
                    folder = "structured"
                    ext = self._get_extension(block.language)
                    filename = f"data_{idx+1:03d}{ext}"
                else:
                    folder = "other"
                    filename = f"block_{idx+1:03d}.txt"
                
                # Track categories
                if folder not in categories:
                    categories[folder] = 0
                categories[folder] += 1
                
                # Add to ZIP
                zip_path_in_archive = f"{folder}/{filename}"
                zipf.writestr(zip_path_in_archive, block.content)
            
            # Add metadata file
            metadata = {
                "source_file": file_meta.original_filename,
                "export_date": str(file_meta.upload_date),
                "total_blocks": len(blocks),
                "categories": categories,
                "blocks": [
                    {
                        "id": block.id,
                        "type": block.block_type,
                        "language": block.language,
                        "confidence": block.confidence_score,
                        "lines": f"{block.start_line}-{block.end_line}"
                    }
                    for block in blocks
                ]
            }
            
            zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        return zip_path

    def _blocks_to_data(self, file_meta: FileMetadata, blocks: List[ExtractedBlock]) -> List[Dict[str, Any]]:
        """Convert blocks to a list of dictionaries for data export."""
        data = []
        for block in blocks:
            item = {
                "file_id": file_meta.id,
                "filename": file_meta.original_filename,
                "file_hash": file_meta.file_hash,
                "upload_date": str(file_meta.upload_date),
                "block_id": block.id,
                "content": block.content,
                "language": block.language,
                "block_type": block.block_type,
                "confidence_score": block.confidence_score,
                "start_line": block.start_line,
                "end_line": block.end_line,
                "validation_method": block.validation_method,
            }
            data.append(item)
        return data

    def generate_jsonl(self, file_meta: FileMetadata, blocks: List[ExtractedBlock]) -> Path:
        """Generate a JSONL export."""
        filename = f"hpes_export_{file_meta.id}_{file_meta.file_hash[:8]}.jsonl"
        path = self.export_dir / filename
        
        data = self._blocks_to_data(file_meta, blocks)
        
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
                
        return path

    def generate_parquet(self, file_meta: FileMetadata, blocks: List[ExtractedBlock]) -> Path:
        """Generate a Parquet export."""
        filename = f"hpes_export_{file_meta.id}_{file_meta.file_hash[:8]}.parquet"
        path = self.export_dir / filename
        
        data = self._blocks_to_data(file_meta, blocks)
        df = pd.DataFrame(data)
        
        # Ensure correct data types for Parquet
        # Parquet has strict typing, so we convert objects to strings where appropriate or letting pandas infer
        # Timestamp needs to be handled if not string
        
        df.to_parquet(path, index=False)
        
        return path
