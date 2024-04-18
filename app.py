import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import datetime

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

def save_word_counts_to_csv(word_counts):
    csv_file = f"/tmp/word_counts_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['word', 'count'])
        writer.writeheader()
        for word, count in word_counts.items():
            writer.writerow({'word': word, 'count': count})
    return csv_file

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
    csv_file = save_word_counts_to_csv(word_counts)
    return {"message": f"Word counts saved to '{csv_file}'."}
