from .parser import Document, Parser
from .etum import parsers as etum_mode
from .cotsq import parsers as cotsq_mode
from . import utils
import logging

logging.basicConfig(filename="debug.log", filemode="w", level=logging.DEBUG)
