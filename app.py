from fastapi import FastAPI, UploadFile, File
from typing import List
import csv
import re

app = FastAPI()

def count_words_in_text(words, text):
    word_counts = {}
    for word in words:
        count = len(re.findall(r'\b' + re.escape(word) + r'\b', text))
        word_counts[word] = count
    return word_counts

@app.post("/count_words")
async def count_words(words: List[str], file: UploadFile = File(...)):
    # Read the uploaded file
    contents = await file.read()
    text = contents.decode("utf-8")
    
    # Count occurrences of words in the text
    word_counts = count_words_in_text(words, text)
    
    # Save word counts to a CSV file
    csv_file = 'word_counts.csv'
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['word', 'count'])
        writer.writeheader()
        for word in words:
            writer.writerow({'word': word, 'count': word_counts.get(word, 0)})
    
    return {"message": f"Word counts saved to '{csv_file}'."}
