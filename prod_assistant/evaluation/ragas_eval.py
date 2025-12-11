import asyncio 
from utils.model_loader import ModelLoader
from ragas import SingleTurnSample 
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper   
from ragas.metrics import LLMContextPrecisionWithoutReference, ResponseRelevancy 
import grc.experimental.aio as grpc_aio 

grpc_aio.init_grpc_aio()
model_loader = ModelLoader()

def evaluate_context_precision(query, response, retrieved_context):
    try:
        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_context=retrieved_context
        )

        async def main():
            llm = model_loader.load_llm()
            evaluator = LangchainLLMWrapper(llm)
            context_precision = LLMContextPrecisionWithoutReference(llm= evaluator)
            result = await context_precision.single_turn_ascore(sample)
            return result
        
        return asyncio.run(main())
    except Exception as e:
        print(f"Error during context precision evaluation: {e}")
        return None
    
def evaluate_response_relevancy(query, response, retrieved_context):
    try:
        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_context=retrieved_context
        )

        async def main():
            llm = model_loader.load_llm()
            embedding_model = model_loader.load_embeddings()
            llm_wrapper = LangchainLLMWrapper(llm)
            embedding_wrapper = LangchainEmbeddingsWrapper(embedding_model)
            relevancy_evaluator = ResponseRelevancy(
                llm=llm_wrapper,
                embedding_model=embedding_wrapper
            )
            result = await relevancy_evaluator.single_turn_ascore(sample)
            return result
        
        return asyncio.run(main()) 
    except Exception as e:
        print(f"Error during response relevancy evaluation: {e}")
        return None