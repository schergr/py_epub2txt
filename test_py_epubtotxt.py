import os
import pytest
from unittest.mock import patch
from py_epubtotxt import process_file

@pytest.fixture
def mock_os_getmtime(monkeypatch):
    def mock_getmtime(file_path):
        return 1234567890.0  # Mock the last modified time
    monkeypatch.setattr(os.path, 'getmtime', mock_getmtime)

def test_process_file_skips_already_processed_file(mock_os_getmtime, capsys):
    processed_files = {'/path/to/file.epub': 1234567890.0}
    file_path = '/path/to/file.epub'
    output_directory = '/path/to/output'
    result = process_file(file_path, output_directory, processed_files)
    captured = capsys.readouterr()
    assert result == 0
    assert captured.out == f"Skipping already processed file: {file_path}\n"

def test_process_file_handles_epub_file(mock_os_getmtime, capsys):
    processed_files = {}
    file_path = '/path/to/file.epub'
    output_directory = '/path/to/output'
    result = process_file(file_path, output_directory, processed_files)
    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == f"Processed: {file_path}\n"
    assert processed_files[file_path] == 1234567890.0

def test_process_file_handles_pdf_file(mock_os_getmtime, capsys):
    processed_files = {}
    file_path = '/path/to/file.pdf'
    output_directory = '/path/to/output'
    result = process_file(file_path, output_directory, processed_files)
    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == f"Processed: {file_path}\n"
    assert processed_files[file_path] == 1234567890.0

def test_process_file_handles_docx_file(mock_os_getmtime, capsys):
    processed_files = {}
    file_path = '/path/to/file.docx'
    output_directory = '/path/to/output'
    result = process_file(file_path, output_directory, processed_files)
    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == f"Processed: {file_path}\n"
    assert processed_files[file_path] == 1234567890.0

def test_process_file_handles_unsupported_file_format(mock_os_getmtime, capsys):
    processed_files = {}
    file_path = '/path/to/file.txt'
    output_directory = '/path/to/output'
    result = process_file(file_path, output_directory, processed_files)
    captured = capsys.readouterr()
    assert result == 0
    assert captured.out == f"Unsupported file format: {file_path}\n"