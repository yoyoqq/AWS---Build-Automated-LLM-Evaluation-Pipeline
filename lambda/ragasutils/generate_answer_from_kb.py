import boto3
from botocore.client import Config
from langchain_aws.chat_models.bedrock import ChatBedrock
from langchain_aws.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from datasets import Dataset

class KnowledgeBasesGenerateAnswer:
    def __init__(self, model_id: str, KB_ID: str):
        self.bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.bedrock_agent_client = boto3.client("bedrock-agent-runtime",
                                                 config=self.bedrock_config)

        self.retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id=KB_ID,
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 10}},
            client=self.bedrock_agent_client)

        self.llm_for_text_generation = ChatBedrock(model_id=model_id, client=self.bedrock_client)

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm_for_text_generation,
            retriever=self.retriever,
            return_source_documents=True)


    # def prepare_evaluation_dataset(self, questions, ground_truths):
    #     generated_answers = []
    #     contexts = []
    #     for query in questions:
    #         generated_answers.append(self.qa_chain.invoke(query)["result"])
    #         contexts.append([docs.page_content for docs in self.retriever.invoke(query)])
    #     # To dict
    #     data = {
    #         "question": questions,
    #         "answer": generated_answers,
    #         "contexts": contexts,
    #         "ground_truth": ground_truths
    #     }
    #     # Convert dict to dataset
    #     return data

    def get_answer_and_context(self, question):
        answer = self.qa_chain.invoke(question)["result"]

        contexts = [docs.page_content for docs in self.retriever.invoke(question)]

        data = {
            "answer": answer,
            "context": contexts,
        }

        return data
