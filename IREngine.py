from tokenize_utils import simpler_tokenization as tokenize, smart_tokenizer as smart_tokenize
from math import log
from scipy import spatial


class IREngine(object):
    """
    The class which represents our Information Retrieval engine.
    A brief review of the properties:
    Documents:
        The documents property look like this:
        {
            "document_id1": <Document Object1>,
            "document_id2": <Document Object2>,
            ...
            "document_id9": <Document Object9>
        }

    Inverted Index:
        The inverted index is used for efficiency purposes on lookups and calculating different TFs/IDFs.
        It looks something like this:
        {
            "term1": {"document_id1": tf(int), "document_id2": tf(int)},
            "term2": {"document_id1": tf(int), "document_id2": tf(int)},
            ...
            "term9": {"document_id1": tf(int), "document_id2": tf(int)}
        }
        We do not store the IDF for each term. It is useless to do so, because calculating the
        length of a dictionary in CPython's implementation (and all other built-in data structures) is O(1).
    """

    def __init__(self):
        self.documents = {}
        self.inverted_index = {}

    def add_document(self, document):
        """
        Adds a document to the documents dictionary of the engine. Also updates the inverted index accordingly.
        :param document: The to-be-indexed document (Document object type).
        """
        if document.doc_id not in self.documents:
            self.documents[document.doc_id] = document
            self.update_inverted_index(document)
            return True
        print 'Error: {} is already indexed. No action will be taken.'.format(document.doc_id)
        return False

    def update_inverted_index(self, document):
        """
        Updates the inverted index when a new document is inserted.
        :param document: The new document (Document object type).
        """
        for term in document.terms:
            if term not in self.inverted_index:
                # If the term is not present, we add it as a key, update doc frequency by one, and the tf for it by one.
                self.inverted_index[term] = {}
            if document.doc_id not in self.inverted_index[term]:
                self.inverted_index[term][document.doc_id] = 1
            else:
                self.inverted_index[term][document.doc_id] += 1

    def free_text_query(self, query_text, num_of_results=5, smart_tokenizer=False):
        """
        A function that implements a simple query with a document text.
        It simply tokenizes the text using the IR's tokenizer, and passes it to the standard term-query.
        :param smart_tokenizer: Determines whether should we use the smart (stemming) tokenizer.
        :param num_of_results: Number of top results to show.
        :param query_text: The query string. Can be a string of any length.
        :returns a list of a documents in descending order of similarity to the input query.
        """
        query_terms = smart_tokenize(query_text) if smart_tokenizer else tokenize(query_text)
        return self.query_by_terms(query_terms, num_of_results)

    def query_by_terms(self, query_terms, num_of_results=5):
        """
        A standard query on the IR engine. Accepts 1 to n query terms.
        :param query_terms: A list containing the terms (string) of the query.
        :param num_of_results: How many results (documents) should be fetched
        :return: A list of the top `num_of_results` relevant documents.
        """
        results = []
        query_tf_idf_vector = self.calculate_tf_idf_for_query(query_terms)
        term_to_idf_mapping = {term: self._calculate_term_idf(term) for term in query_terms}
        relevant_doc_ids = self._get_relevant_doc_ids(query_terms)
        for doc_id in relevant_doc_ids:
            document = self.documents[doc_id]
            document_vector = []
            for query_term in query_terms:
                # "I love all the restaurants, I especially recommend trying McDonalds"
                # [[x,y], [a,b], [c,d]]
                query_tf = 0
                if query_term in self.inverted_index:
                    query_tf = float(self.inverted_index[query_term].get(document.doc_id, 0)) / len(document.terms)
                query_idf = term_to_idf_mapping[query_term]
                document_vector.append(query_tf * query_idf)
            similarity = 1 - spatial.distance.cosine(query_tf_idf_vector, document_vector)
            results.append((document, similarity))
        if num_of_results > len(results):
            num_of_results = len(results)
        top_results = sorted(results, key=lambda tup: tup[1], reverse=True)[:num_of_results]
        return [str(top_result[0]) for top_result in top_results[:num_of_results]]

    def _get_relevant_doc_ids(self, terms):
        """
        Retrieves the relevant document ids from the documents dictionary.
        This is useful for optimization purposes because in most of the queries, the terms
        Are not present in all of the indexed documents.
        Eliminating most of them by checking it with the inverted index, and applying TF*IDF only to the relevant ones
        is effective and time-saving.
        :param terms: The terms given in a query.
        :returns a list of doc_ids (strings) that are relevant to the query (as in they have at least one term
        associated with the query).
        """
        relevant_docs = set()
        for term in terms:
            if term in self.inverted_index:
                [relevant_docs.add(doc_id) for doc_id in self.inverted_index[term].iterkeys()]
        return relevant_docs

    def _calculate_term_idf(self, term):
        """
        Calculates IDF for a given term. I chose the normalization method of taking the natural log
        of (total number of documents) / (number of docs with term) because it is simple to implement and
        is considered one of the most effective normalization techniques.
        :param term: The term
        :return: A normalized IDF value.
        """
        num_of_docs_with_term = len(self.inverted_index.get(term, {}))
        if term in self.inverted_index:
            return 1.0 + log(float(len(self.documents)) / num_of_docs_with_term)
        return 1.0

    def calculate_tf_idf_for_query(self, query_terms):
        """
        Calculates TF*IDF for a query, by creating a small mapped inverted index for the query (to get the tf),
        deriving and computing the formula's values from it.
        :param query_terms: The query terms (list of strings)
        :return: A list of numbers which represents the TF*IDF vector of the query.
        """
        query_term_frequencies = {}
        query_vector = []
        # First create the tf mapping for each term
        for query_term in query_terms:
            if query_term not in query_term_frequencies:
                query_term_frequencies[query_term] = 1
            else:
                query_term_frequencies[query_term] += 1
        # Use the mapping to compute TF*IDF for the query
        for query_term in query_terms:
            term_tf = float(query_term_frequencies[query_term]) / len(query_terms)
            term_idf = self._calculate_term_idf(query_term)
            query_vector.append(term_tf * term_idf)
        return query_vector
