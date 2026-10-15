import sys
import os
sys.path.append(os.path.dirname(__file__))

from rag_pipeline import retrieve_chunks, load_all_data

# example set — apne questions se bhara
eval_set = [

    # Computer Networks
    {"q": "What is CSMA/CD?", "subject": "Computer_Network"},
    {"q": "What is the OSI model?", "subject": "Computer_Network"},
    {"q": "What is TCP?", "subject": "Computer_Network"},
    {"q": "What is an IP address?", "subject": "Computer_Network"},
    {"q": "What is the difference between TCP and UDP?", "subject": "Computer_Network"},

    # DBMS
    {"q": "What is a primary key?", "subject": "DBMS"},
    {"q": "What is a foreign key?", "subject": "DBMS"},
    {"q": "What is normalization in DBMS?", "subject": "DBMS"},
    {"q": "What is a relational database?", "subject": "DBMS"},
    {"q": "What is SQL?", "subject": "DBMS"},

    # DSA
    {"q": "What is binary search?", "subject": "DSA"},
    {"q": "What is a stack?", "subject": "DSA"},
    {"q": "What is a queue?", "subject": "DSA"},
    {"q": "What is the time complexity of binary search?", "subject": "DSA"},
    {"q": "What is an array?", "subject": "DSA"},

    # Discrete Mathematics
    {"q": "What is the pigeonhole principle?", "subject": "Descrete_Mathematics"},
    {"q": "What is a proposition?", "subject": "Descrete_Mathematics"},
    {"q": "What is a set?", "subject": "Descrete_Mathematics"},
    {"q": "What is a graph in discrete mathematics?", "subject": "Descrete_Mathematics"},
    {"q": "What is a relation between two sets in discrete mathematics?", "subject": "Descrete_Mathematics"},

    # Data Science
    {"q": "What is exploratory data analysis?", "subject": "Data_Science_&_Visualization"},
    {"q": "What is mean, median and mode?", "subject": "Data_Science_&_Visualization"},
    {"q": "What is standard deviation?", "subject": "Data_Science_&_Visualization"},
    {"q": "What is data visualization?", "subject": "Data_Science_&_Visualization"},
    {"q": "What is a histogram?", "subject": "Data_Science_&_Visualization"},
]

chunks, index, model = load_all_data()
hits = 0

for item in eval_set:
    retrieved = retrieve_chunks(item["q"], model, index, chunks, top_k=4)
    subjects = [r["subject"] for r in retrieved]
    ok = item["subject"] in subjects
    hits += 1 if ok else 0
    print(("OK" if ok else "MISS"), item["q"][:50], "->", subjects[0])

print(f"\nRecall@4 (subject): {hits}/{len(eval_set)} = {hits/len(eval_set):.2f}")