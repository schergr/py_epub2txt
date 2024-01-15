import ebooklib
import os
import json
import PyPDF2

from zipfile import BadZipFile
from ebooklib import epub
from bs4 import BeautifulSoup
from docx import Document
from markdownify import markdownify as md

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
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                try:
                    text += page.extract_text() + "\n"
                except Exception as e:
                    print(f"Error extracting text from page in {pdf_path}: {e}")
    except Exception as e:
        print(f"Error reading PDF file {pdf_path}: {e}")
    return text

def epub2thtml(epub_path):
    try:
        book = epub.read_epub(epub_path,{"ignore_ncx": True})
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapters.append(item.get_content())
        return chapters
    except BadZipFile:
        print(f"Bad Zip File: {epub_path} - Skipping this file.")
        return []
    except Exception as e:
        print(f"Error processing {epub_path}: {e}")
        return []

def chap2text(chap):
    soup = BeautifulSoup(chap, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def thtml2ttext(thtml):
    Output = []
    for html in thtml:
        text = chap2text(html)
        Output.append(text)
    return Output

def docx_to_markdown(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    doc_ text = '\n'.join(full_text)
    return md(doc_text)

def epub2text(epub_path):
    chapters = epub2thtml(epub_path)
    ttext = thtml2ttext(chapters)
    return ttext
    
def process_file(file_path, output_directory, processed_files):

    last_modified = os.path.getmtime(file_path)
    if file_path in processed_files and processed_files[file_path] == last_modified:
        print(f"Skipping already processed file: {file_path}")
        return 0
    # Determine the file type and process accordingly
    if file_path.endswith('.epub'):
        #chapters = epub2thtml(file_path)
        #if not chapters:  # Check if chapters list is empty
        #    return 0  # Skip further processing
        text_content = epub2text(file_path)
    elif file_path.endswith('.pdf'):
        text_content = pdf2text(file_path)
    elif file_path.endswith('.docx'):
        text_content = docx_to_markdown(file_path)
    else:
        print(f"Unsupported file format: {file_path}")
        return 0
    # Write the extracted text to a file in the output directory
    output_file_name = os.path.splitext(os.path.basename(file_path))[0] + '.txt'
    output_file_path = os.path.join(output_directory, output_file_name)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        #f.write('\n'.join(text_content))
        f.write(text_content)
    print(f"Processed: {file_path}")

    processed_files[file_path] = last_modified
    return 1
    
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
            file_path = os.path.join(root, file)
            print (f"Processing file: {file_path}")
            if file.endswith('.epub'):
                processed_count += process_file(file_path, output_directory, processed_files)
                write_processed_files_info(processed_files_path, processed_files)  # Update the JSON after each file
            elif file.endswith('.pdf'):
                processed_count += process_file(file_path, output_directory, processed_files)
                write_processed_files_info(processed_files_path, processed_files)  # Update the JSON after each file
            elif file.endswith('.docx'):
                processed_count += process_file(file_path, output_directory, processed_files)    
                write_processed_files_info(processed_files_path, processed_files)  # Update the JSON after each file
    #write_processed_files_info(processed_files_path, processed_files)
    print(f"Total processed files: {processed_count}")

if __name__ == "__main__":
    main()