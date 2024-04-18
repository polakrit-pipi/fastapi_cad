from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import csv
import datetime
import re
from pathlib import Path

app = FastAPI()

def count_word_occurrences(word, text):
    count = 0
    start_index = 0
    
    while True:
        next_index = text.find(word, start_index)
        if next_index == -1:
            break
        count += 1
        start_index = next_index + len(word)
    
    return count

def read_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def count_words_in_file(words, text):
    word_counts = {}
    for word in words:
        count = count_word_occurrences(word, text)
        word_counts[word] = count
    return word_counts

def save_word_counts_to_csv(word_counts, csv_file):
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['word', 'count'])
        writer.writeheader()
        for word, count in word_counts.items():
            writer.writerow({'word': word, 'count': count})

class WordCountRequest(BaseModel):
    file_path: str
    words_to_count: list

@app.post("/wordcount/")
async def word_count(request: WordCountRequest):
    text = read_text_from_file(request.file_path)
    word_counts = count_words_in_file(request.words_to_count, text)
    return word_counts

@app.post("/wordcount/csv/")
async def word_count_to_csv(request: WordCountRequest):
    text = read_text_from_file(request.file_path)
    word_counts = count_words_in_file(request.words_to_count, text)
    csv_file = f"word_counts_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    save_word_counts_to_csv(word_counts, csv_file)
    return {"message": f"Word counts saved to '{csv_file}'."}

@app.post("/count_words")
async def count_words(words: List[str], file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        contents = await file.read()
        text = contents.decode("utf-8")
        
        # Count occurrences of words in the text
        word_counts = count_words_in_text(words, text)
        
        # Modify counts for consecutive occurrences of words
        for word in words:
            consecutive_count = len(re.findall(r'\b' + re.escape(word) + r'(?:\s+' + re.escape(word) + r')*\b', text))
            word_counts[word] += consecutive_count - 1  # Subtract 1 to account for initial count
        
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Create a new file name with timestamp
        csv_file = f'word_counts_{timestamp}.csv'
        
        # Get the absolute path of the file
        csv_file_path = str(Path.cwd() / csv_file)
        
        # Write word counts to the new CSV file
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['word', 'count'])
            writer.writeheader()
            for word, count in word_counts.items():
                writer.writerow({'word': word, 'count': count})
        
        return {"message": f"Word counts saved to '{csv_file}'.", "file_path": csv_file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
