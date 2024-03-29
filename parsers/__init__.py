from .parser import Document, Parser
from .etum import parsers as etum_mode
from .cotsq import parsers as cotsq_mode
from .srd import parsers as srd_mode
from .cotsq_long import parsers as cotsq_long_mode
from . import utils
import logging

logging.basicConfig(filename="debug.log", filemode="w", level=logging.DEBUG)
