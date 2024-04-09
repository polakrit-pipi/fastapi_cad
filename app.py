from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import csv
import re
from datetime import datetime
from pathlib import Path

app = FastAPI()

def count_words_in_text(words, text):
    word_counts = {}
    for word in words:
        count = len(re.findall(r'\b' + re.escape(word) + r'\b', text))
        word_counts[word] = count
    return word_counts

@app.post("/count_words")
async def count_words(words: List[str], file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        contents = await file.read()
        text = contents.decode("utf-8")
        
        # Count occurrences of words in the text
        word_counts = count_words_in_text(words, text)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Specify the directory where you want to save the file
        save_directory = "./"
        
        # Create a new file name with timestamp
        csv_file = f'word_counts_{timestamp}.csv'
        
        # Get the absolute path of the file
        csv_file_path = str(Path(save_directory) / csv_file)
        
        # Write word counts to the new CSV file
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['word', 'count'])
            writer.writeheader()
            for word in words:
                writer.writerow({'word': word, 'count': word_counts.get(word, 0)})
        
        return {"message": f"Word counts saved to '{csv_file}'.", "file_path": csv_file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
