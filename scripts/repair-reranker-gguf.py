"""Format-only repair matching pinned llama.cpp conversion/qwen.py. No training."""
from pathlib import Path
import gguf,numpy as np,hashlib,json
root=Path(__file__).resolve().parents[1]
src=root/'models/reranker/Qwen3-Reranker-0.6B-q8_0.gguf';dst=root/'models/reranker/Qwen3-Reranker-0.6B-rank-q8_0.gguf'
r=gguf.GGUFReader(str(src));w=gguf.GGUFWriter(str(dst),'qwen3')
for f in r.fields.values():
    if f.name.startswith(('GGUF.','tokenizer.chat_template')) or f.name in ['general.architecture','qwen3.pooling_type','classifier.output_labels']:continue
    w.add_key_value(f.name,f.contents(),f.types[0],sub_type=f.types[-1] if f.types[0]==gguf.GGUFValueType.ARRAY else None)
w.add_pooling_type(gguf.PoolingType.RANK);w.add_classifier_output_labels(['yes','no'])
w.add_chat_template([{'name':'rerank','template':'<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n<Instruct>: Given a web search query, retrieve relevant passages that answer the query\n<Query>: {query}\n<Document>: {document}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'}])
tokens=r.fields['tokenizer.ggml.tokens'].contents();ids=[tokens.index('yes'),tokens.index('no')]
head=next((t for t in r.tensors if t.name=='output.weight'),None)
if head is None:head=next(t for t in r.tensors if t.name=='token_embd.weight')
cls=gguf.quants.dequantize(head.data[ids],head.tensor_type).astype(np.float32)
assert cls.shape==(2,1024),cls.shape
for t in r.tensors:
    if t.name=='output.weight':continue
    w.add_tensor(t.name,t.data,raw_dtype=t.tensor_type)
w.add_tensor('cls.output.weight',cls)
w.write_header_to_file();w.write_kv_data_to_file();w.write_tensors_to_file();w.close()
with dst.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
m=json.loads((root/'docs/MODEL-MANIFEST.json').read_text());m['reranker']['original_file']=str(src.relative_to(root));m['reranker']['original_sha256']='8b5337e5baadf83fdd6f7a865dde4b3627fc53a1c8e56cc2f83260dfdd089c49';m['reranker'].update(file=str(dst.relative_to(root)),sha256=sha,conversion='scripts/repair-reranker-gguf.py; exact yes/no head extraction from quantized output, no training',token_ids=ids)
(root/'docs/MODEL-MANIFEST.json').write_text(json.dumps(m,indent=2));print('Repaired rank head',ids,sha)
