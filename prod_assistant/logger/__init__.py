# create a object of the custom looger 
# no need to create again and again 

from .custom_logger import CustomLogger
GLOBAL_LOGGER = CustomLogger().get_logger('prod_assistant')