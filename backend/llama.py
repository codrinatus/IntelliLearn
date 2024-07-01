import codecs
import json
import os
import re
import time
import asyncio

from langchain.chains import RetrievalQA
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


def generator(input):
    start_time = time.time()  # starting a timer to check how much time it takes to generate questions
    ollama = Ollama(
        base_url='http://localhost:11434',
        model="llama3",
        keep_alive=-1
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                   chunk_overlap=20)  # we split the text into smaller pieces
    all_splits = text_splitter.split_text(input)

    oembed = OllamaEmbeddings(base_url="http://localhost:11434", model="nomic-embed-text")  # we create embeddings
    vectorstore = Chroma.from_texts(texts=all_splits, embedding=oembed)
    qachain = RetrievalQA.from_chain_type(ollama,
                                          retriever=vectorstore.as_retriever())

    query = '''Generate Questions with multiple choice answers from this data structure course ignoring details about 
    the faculty.Indicate the correct answer.Make sure you generate 
    easy, medium and hard difficulty questions.Follow the following JSON format:

{
    "questionnumber": "1",
    "question": "What is the time complexity of binary search?",
    "choiceA": "O(n)",
    "choiceB": "O(log n)",
    "choiceC": "O(n log n)",
    "choiceD": "O(n^2)",
    "correctchoiceletter": "B",
    "difficulty": "medium"
}

The JSON format should be strictly followed. Here is another example:

{
    "questionnumber": "2",
    "question": "What does CPU stand for?",
    "choiceA": "Central Process Unit",
    "choiceB": "Central Processing Unit",
    "choiceC": "Computer Personal Unit",
    "choiceD": "Central Processor Unit",
    "correctchoiceletter": "B",
    "difficulty": "easy"
} "

Please generate as many questions as you can:
'''

    result = qachain.invoke({"query": query})['result']

    end_time = time.time()  # ending the timer
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60

    decoded_result = codecs.decode(result, 'unicode_escape')  # we make the text readable
    time_text = f"\n================================\nQuestion generation took {minutes} minutes and {seconds:.2f} seconds"

    existing_files = os.listdir("output")
    # numbers = [int(f.split('_')[1].split('.')[0]) for f in existing_files if
    #            f.startswith("questions") and f.endswith(".txt")]
    # nr = max(numbers, default=0) + 1
    print(decoded_result + time_text)
    # with open("output/", 'w', encoding='utf-8') as txt_file:
    #     txt_file.write(decoded_result)

    text = decoded_result.replace("\n", "")
    json_objects = re.findall(r'\{[^}]+\}', text)
    questions = []
    for obj in json_objects:
        question_data = json.loads(obj)
        questions.append(question_data)

    json_result = {
        "questions": questions,
        "time": {
            "minutes": minutes,
            "seconds": seconds
        }
    }

    return json_result

