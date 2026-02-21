from openai import OpenAI
class AnswerQuestions:
    def __init__(self, vector_store,client: OpenAI):
        self.vector_store = vector_store
        self.client = client

    def answer_query(self, query: str,user_id: str = 'gyanko_user_id'):
        index_name = "gyankofirstdraft"
        index = self.vector_store.pc.Index(index_name)

        # create embedding for the query
        query_embedding = self.vector_store.text_processor.embed_text(query)

        # search the index
        res = index.query(vector=query_embedding, top_k=5, include_metadata=True, filter={"user_id": user_id}, namespace="gyankoSpace")

        context = "\n".join([match.metadata["chunk"] for match in res.matches])

        prompt = f"""
        Use the following context to answer the question:
        {context}

        Question: {query}
        """
        response = self.client.responses.create(
            model="gpt-4o",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                ],
            }]
        )
        return response.output_text