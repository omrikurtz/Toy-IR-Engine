"""Main script for running the IR-Engine. Dependencies and how-tos can be found in the README.txt"""

from document import Document
from IREngine import IREngine
import csv

DATASET_FILE_NAME = 'tweets.csv'

documents = {}
with open(DATASET_FILE_NAME, 'rb') as dataset:
    csv_reader = csv.reader(dataset)
    header = next(csv_reader)
    for i in xrange(1000):  # Load first 1000 documents
        row = next(csv_reader)
        documents[row[0]] = row[5].replace("\"", "").replace("\'", "")
    # documents = {row[0]: row[5].replace("\"", "").replace("\'", "") for row in csv_reader} - Loads all documents

search_engine = IREngine()
print 'Welcome to Simple-Search!'
print 'Processing documents. This might take a while.'
for document_id, text in documents.iteritems():
    search_engine.add_document(Document(document_id, text))
print 'Done!'
while True:
    query = raw_input("Enter your query: ")
    num_of_results = int(raw_input("How many results show be fetched? : "))
    results = search_engine.free_text_query(query, num_of_results)
    for num, result in enumerate(results):
        print '{0}: {1}'.format(num+1, result)


