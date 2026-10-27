#!/usr/bin/env python3
"""Build compressed full-text index with source-line snippets for Lagale pages."""
from html.parser import HTMLParser
from pathlib import Path
from collections import defaultdict
import json,re,gzip,html as html_lib
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'docs'; GZ=DOCS/'search-index.json.gz'
BLOCKS={'p','div','section','article','li','h1','h2','h3','h4','h5','tr','br','td','th'}
class Parser(HTMLParser):
 def __init__(self): super().__init__(convert_charrefs=True); self.parts=[]; self.blocks=[]; self.buf=[]; self.title=[]; self.in_title=False; self.hidden=[]
 def flush(self):
  s=norm(' '.join(self.buf)); self.buf=[]
  if len(s)>2:self.blocks.append(s)
 def handle_starttag(self,t,a):
  if t in ('script','style','noscript','svg'): self.hidden.append(t)
  if t=='title': self.in_title=True
  if t in BLOCKS and not self.hidden:self.flush()
 def handle_endtag(self,t):
  if t in ('script','style','noscript','svg'):
   if t in self.hidden:self.hidden.reverse();self.hidden.remove(t);self.hidden.reverse()
  if t=='title':self.in_title=False
  if t in BLOCKS and not self.hidden:self.flush()
 def handle_data(self,d):
  if self.hidden:return
  d=d.strip()
  if d:self.buf.append(d); self.title.append(d) if self.in_title else None

def norm(s): return re.sub(r'[\u200b\ufeff\s]+',' ',html_lib.unescape(s)).strip()
def quiz_lines(raw):
 lines=[]
 # Preserve each question object as a searchable source line instead of mixing all questions together.
 for m in re.finditer(r'(?:let|const|var)\s+allQuestionsData\s*=\s*\[',raw):
  start=m.end(); depth=1; quote=''; esc=False; objstart=None
  for i in range(start,len(raw)):
   c=raw[i]
   if quote:
    if esc:esc=False
    elif c=='\\':esc=True
    elif c==quote:quote=''
    continue
   if c in ('"',"'"):quote=c;continue
   if c=='{' and depth==1:objstart=i
   elif c=='[':depth+=1
   elif c==']':
    depth-=1
    if depth==0:
     if objstart is not None: pass
     break
   elif c=='}' and depth==1 and objstart is not None:
    chunk=raw[objstart:i+1]; objstart=None
    vals=[]
    for sm in re.finditer(r'''("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')''',chunk):
     token=sm.group(0)
     try:v=json.loads(token) if token[0]=='"' else token[1:-1]
     except Exception:v=token[1:-1]
     v=norm(v)
     if len(v)>1:vals.append(v)
    line=norm(' — '.join(vals))
    if line:lines.append(line)
 return lines

docs=[]; postings=defaultdict(list)
for f in DOCS.rglob('*.html'):
 raw=f.read_text(encoding='utf-8',errors='ignore'); p=Parser(); p.feed(raw); p.flush()
 title=norm(' '.join(p.title)) or f.parent.name.replace('-',' ').title()
 lines=[]
 for line in p.blocks+quiz_lines(raw):
  line=norm(line)
  if line and (not lines or line!=lines[-1]):lines.append(line)
 if not lines:continue
 rel='/'+f.relative_to(DOCS).as_posix()
 if rel.endswith('/index.html'):rel=rel[:-10]
 if rel=='/index.html':rel='/'
 doc_id=len(docs);docs.append({'title':title,'url':rel,'lines':lines})
 seen=set()
 for line_no,line in enumerate(lines):
  for token in set(re.findall(r'[\w\u0900-\u097f]+',line.casefold(),flags=re.UNICODE)):
   if len(token)>1 and (token,line_no) not in seen:
    postings[token].append([doc_id,line_no]);seen.add((token,line_no))
data={'version':2,'docs':docs,'terms':postings}
raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
with gzip.open(GZ,'wb',compresslevel=1) as f:f.write(raw)
print(f'Indexed {len(docs)} HTML pages and {len(postings):,} unique terms with source snippets; compressed {GZ.stat().st_size:,} bytes (raw {len(raw):,}).')
