import ebooklib
import logging
import os
import json
import PyPDF2

from datetime import datetime
from ebooklib import epub
from bs4 import BeautifulSoup

def read_processed_files_info(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {}
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {file_path}. Starting with an empty dictionary.")
        return {}

def write_processed_files_info(file_path, info):
    with open(file_path, 'w') as file:
        json.dump(info, file)

def pdf2text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        for page in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page).extractText() + "\n"
    return text

def epub2thtml(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters

def chap2text(chap):
    soup = BeautifulSoup(chap, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def thtml2ttext(thtml):
    Output = []
    for html in thtml:
        text = chap2text(html)
        Output.append(text)
    return Output

def epub2text(epub_path):
    chapters = epub2thtml(epub_path)
    ttext = thtml2ttext(chapters)
    return ttext

def process_epub_file(epub_file, output_directory, processed_files):
    last_modified = os.path.getmtime(epub_file)
    if epub_file in processed_files and processed_files[epub_file] == last_modified:
        print(f"Skipping already processed file: {epub_file}")
        return 0
    try:
        text_content = epub2text(epub_file)
        output_file_name = os.path.splitext(os.path.basename(epub_file))[0] + '.txt'
        output_file_path = os.path.join(output_directory, output_file_name)

        with open(output_file_path, 'w', encoding='utf-8') as f:
            for chapter in text_content:
                f.write(chapter + "\n")
        print(f"Processed: {epub_file}")
        processed_files[epub_file] = last_modified
        return 1
    except Exception as e:
        print(f"Failed to process {epub_file}: {e}")
        return 0

def main():
    root_epub_dir = "G:\\My Drive\\My Books\\"
    root_txt_output_dir = "G:\\My Drive\\My Books\\output_txt\\"
    input_directory = root_epub_dir
    output_directory = root_txt_output_dir

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    processed_files_path = os.path.join(root_txt_output_dir, 'processed_files.json')
    processed_files = read_processed_files_info(processed_files_path)
    
    processed_count = 0
    for root, dirs, files in os.walk(input_directory):
        if 'output_txt' in dirs:
            dirs.remove('output_txt')
        for file in files:
            if file.endswith('.epub'):
                epub_file_path = os.path.join(root, file)
                processed_count += process_epub_file(epub_file_path, output_directory, processed_files)
    write_processed_files_info(processed_files_path, processed_files)
    print(f"Total processed files: {processed_count}")

if __name__ == "__main__":
    main()