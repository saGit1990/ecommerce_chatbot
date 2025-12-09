from enum import Enum
from typing import Dict
import string 

class PromptType(str, Enum):
    PRODUCT_BOT = 'product_bot'

class PromptTemplate:
    """Class to hold prompt template strings and their metadata"""
    def __init__(self, template:str, description:str = '', version:str = 'v1'):
        self.template = template 
        self.description = description
        self.version = version 

    def format(self, **kwargs) -> str:
        # validate placeholders before forecasting 
        missing = [ f for f in self.required_placeholders() if f not in kwargs ]

        if missing:
            raise ValueError(f'Missing placeholders for prompt formatting: {missing}')
        return self.template.format(**kwargs)
    
    def required_placeholders(self):
        return [field_name for _, field_name, _, _ in string.Formatter().parse(self.template) if field_name]
    

# Central Registry
PROMPT_REGISTRY: Dict[PromptType, PromptTemplate]= {
    PromptType.PRODUCT_BOT: PromptTemplate(
        template=(
            """ 
            You are an expert EcommerceBot specialized in product recommendations and handling customer queries.
            Analyze the provided product titles, ratings, and reviews to provide accurate, helpful response.
            Stay relevant to the context, and keep you answers concise and informative.


            CONTEXT:
            {context}

            QUESTION:
            {question}

            YOUR ANSWER:
            """
        ),
        description="Prompt template for a product assistant bot to answer user queries based on product details and reviews."
    )
}