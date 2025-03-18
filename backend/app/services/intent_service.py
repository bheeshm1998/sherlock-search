# backend/app/services/intent_service.py

import re
from typing import List, Tuple


class IntentService:
    """
    Service to validate user intent and filter queries based on their relevance.
    """

    def __init__(self, vector_database, allowed_contexts: List[str]):
        """
        Initializes the intent service.

        :param vector_database: Vector database client (e.g., Pinecone)
        :param allowed_contexts: List of allowed contexts to validate user intent
        """
        self.vector_database = vector_database
        self.allowed_contexts = allowed_contexts

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Validates whether the given query is acceptable based on its intent.

        :param query: User query
        :return: A tuple (is_valid: bool, reason: str)
        """
        # Rule 1: Prevent any attempts to modify prompts or inject commands
        if self._is_jailbreak_attempt(query):
            return False, "Query contains forbidden override patterns or jailbreak attempts."

        # Rule 2: Ensure query matches a valid context in vector database
        if not self._is_query_relevant_to_data(query):
            return False, "Query is not relevant to the uploaded documents."

        return True, "Query is valid and passes the intent check."

    def _is_jailbreak_attempt(self, query: str) -> bool:
        """
        Checks for unsafe patterns that could attempt to override prompts or execute malicious actions.

        :param query: User query
        :return: True if jailbreak attempt is detected, otherwise False
        """
        # Define forbidden patterns (expand as necessary)
        forbidden_patterns = [
            r"(override|bypass|ignore)",  # Trying to bypass filters
            r"(^!|^\/)",  # Command injection
            r"(system\s+message|prompt\s+rules)"  # Referring to internal application logic
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False

    def _is_query_relevant_to_data(self, query: str) -> bool:
        """
        Validates if the query is contextually relevant to the data in the vector database.

        :param query: User query
        :return: True if the query matches allowed contexts or relevant data, otherwise False
        """
        # Search in vector database using the query
        # Example: Check if query matches allowed documents/topics
        search_results = self.vector_database.query(query, top_k=3)

        # If no results or results with low relevance, the query is invalid
        if not search_results or all(sr["score"] < 0.5 for sr in search_results):
            return False

        # Compare query context to a set of allowed predefined contexts
        for context in self.allowed_contexts:
            if context.lower() in query.lower():
                return True

        return False
