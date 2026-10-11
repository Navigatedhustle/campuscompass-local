"""Scope is established by the caller before this module sees any records."""
import sqlite3,re,json
from .local_models import embedding,rerank

def retrieve(question,docs,cache,cache_scope):
    db=sqlite3.connect(':memory:');db.execute('CREATE VIRTUAL TABLE permitted USING fts5(id UNINDEXED,text)')
    db.executemany('INSERT INTO permitted VALUES (?,?)',[(d['source_id'],d['text']) for d in docs])
    terms=re.findall(r'[A-Za-z0-9]+',question)
    query=' OR '.join('"'+t+'"' for t in terms[:40]) or '"graduation"'
    lexical=[r[0] for r in db.execute('SELECT id FROM permitted WHERE permitted MATCH ? ORDER BY bm25(permitted) LIMIT 20',(query,))];db.close()
    q=embedding('Instruct: Retrieve university records and policies that answer the advising question\nQuery: '+question)
    scores=[]
    for d in docs:
        key=cache_scope+':'+d['hash']
        if key not in cache:cache[key]=embedding(d['text'])
        scores.append((sum(a*b for a,b in zip(q,cache[key])),d['source_id']))
    semantic=[i for _,i in sorted(scores,reverse=True)[:20]]
    fusion={d['source_id']:sum(1/(60+rank.index(d['source_id'])+1) for rank in [lexical,semantic] if d['source_id'] in rank) for d in docs}
    candidates=sorted(docs,key=lambda d:fusion[d['source_id']],reverse=True)[:20]
    ranked=rerank(question,candidates)
    return ranked,{'lexical':lexical,'semantic':semantic,'rrf':fusion,'reranked':[d['source_id'] for d in ranked]}
