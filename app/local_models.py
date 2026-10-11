import httpx,math

def call(port,path,payload):
    # Hard-coded loopback endpoints; no provider configuration or hosted fallback.
    with httpx.Client(trust_env=False,timeout=120) as client:
        response=client.post(f'http://127.0.0.1:{port}{path}',json=payload)
        response.raise_for_status();return response.json()

def embedding(text):
    data=call(8082,'/v1/embeddings',{'input':text,'model':'embedding'})
    v=data['data'][0]['embedding'];norm=math.sqrt(sum(x*x for x in v))
    if len(v)!=1024 or not norm or any(not math.isfinite(x) for x in v):raise ValueError('Invalid local embedding')
    return [x/norm for x in v]

def rerank(question,docs):
    result=call(8083,'/v1/rerank',{'query':question,'documents':[d['text'] for d in docs],'top_n':len(docs)})
    rows=result.get('results',result.get('data',[]))
    if len(rows)!=len(docs):raise ValueError('Incomplete local reranking')
    return [{**docs[r['index']],'relevance':r['relevance_score']} for r in rows]

def generate(messages,schema):
    return call(8081,'/v1/chat/completions',{'model':'campuscompass-qwen','messages':messages,'max_tokens':400,'temperature':0.7,'top_p':0.8,'top_k':20,'min_p':0,'presence_penalty':1.5,'response_format':{'type':'json_schema','json_schema':{'name':'bounded_output','strict':True,'schema':schema}}})
