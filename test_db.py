"""
파일 기반 DB 테스트 코드
"""

from tinydb import TinyDB, Query
from tinydb.operations import delete, increment, decrement, add, subtract, set
from tinydb.table import Document

# https://tinydb.readthedocs.io/en/latest/usage.html

db = TinyDB('./db.json')
db.upsert(Document({'name': 'John', 'age': 22}, doc_id=12))
db.upsert(Document({'name': 'John', 'age': 23}, doc_id=12))
db.upsert(Document({'name': 'John', 'age': 23, 'date':'20220101111111'}, doc_id=12))
