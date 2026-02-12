import pytest
import json
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.services.export_service import ExportService
from app.models import FileMetadata, ExtractedBlock

@pytest.fixture
def mock_export_dir(tmp_path):
    return tmp_path

@pytest.fixture
def export_service(mock_export_dir):
    return ExportService(mock_export_dir)

@pytest.fixture
def mock_data():
    file_meta = FileMetadata(
        id=1,
        filename="test.py",
        original_filename="test.py",
        file_hash="abc123hash",
        upload_date=datetime.now()
    )
    
    blocks = [
        ExtractedBlock(
            id=101,
            file_id=1,
            content="def hello():\n    print('world')",
            language="python",
            block_type="code",
            confidence_score=0.95,
            start_line=1,
            end_line=2,
            validation_method="tree-sitter"
        ),
        ExtractedBlock(
            id=102,
            file_id=1,
            content='{"key": "value"}',
            language="json",
            block_type="config",
            confidence_score=0.99,
            start_line=5,
            end_line=5,
            validation_method="json-parser"
        )
    ]
    return file_meta, blocks

def test_generate_jsonl(export_service, mock_data):
    file_meta, blocks = mock_data
    path = export_service.generate_jsonl(file_meta, blocks)
    
    assert path.exists()
    assert path.suffix == ".jsonl"
    
    with open(path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2
        
        item1 = json.loads(lines[0])
        assert item1['block_id'] == 101
        assert item1['language'] == 'python'
        assert item1['content'] == "def hello():\n    print('world')"
        
        item2 = json.loads(lines[1])
        assert item2['block_id'] == 102
        assert item2['block_type'] == 'config'

def test_generate_parquet(export_service, mock_data):
    file_meta, blocks = mock_data
    path = export_service.generate_parquet(file_meta, blocks)
    
    assert path.exists()
    assert path.suffix == ".parquet"
    
    df = pd.read_parquet(path)
    assert len(df) == 2
    assert df.iloc[0]['block_id'] == 101
    assert df.iloc[0]['language'] == 'python'
    assert df.iloc[1]['block_type'] == 'config'

def test_generate_zip(export_service, mock_data):
    file_meta, blocks = mock_data
    path = export_service.generate_zip(file_meta, blocks)
    
    assert path.exists()
    assert path.suffix == ".zip"
    
    # Optional: could use zipfile module to verify contents if needed
