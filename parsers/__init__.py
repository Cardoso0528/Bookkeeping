from .base_parser import BankStatementParser
from .comerica_parser import ComericaParser
from .prosperity_parser import ProsperityParser

# List of all available parsers
AVAILABLE_PARSERS = [
    ComericaParser,
    ProsperityParser
]