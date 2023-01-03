from .py import Trie as PyTrie

Trie = PyTrie

# pylint:disable=wrong-import-position
try:
    from .datrie import Trie as DATrie
except ImportError:
    pass
else:
    Trie = DATrie
# pylint:enable=wrong-import-position
