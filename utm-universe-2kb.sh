#!/bin/sh
exec python3 -u -c 'import os,json,time,hashlib;from http.server import*;S="/data/cosmic-love-state.json";J="/data/cosmic-love-operations.jsonl";R="/data/residents.json";P=int(os.getenv("PORT","8080"));M=2000;exec("""def rd(p,d):
 try:return json.load(open(p))
 except:return d
def wr(p,x):
 open(p,"w").write(json.dumps(x,separators=(",",":")))
def tm(p,i,l):
 r={}
 for x in p.split(";"):
  a=x.split(",");r[(a[0],a[1])]=a[2:]
 q="0";h=t=0;T={k:c for k,c in enumerate(i) if c!="_"}
 while t<min(int(l),M):
  z=r.get((q,T.get(h,"_")))
  if not z:break
  q,w,d=z;T.pop(h,None) if w=="_" else T.__setitem__(h,w);h+=(d=="R")-(d=="L");t+=1
 A=list(T)or[0];return {"q":q,"h":h,"t":t,"tape":"".join(T.get(k,"_") for k in range(min(A),max(A)+1))}
class H(BaseHTTPRequestHandler):
 def out(s,x,c=200):
  b=json.dumps(x,separators=(",",":")).encode();s.send_response(c);s.send_header("Content-Type","application/json");s.end_headers();s.wfile.write(b)
 def do_GET(s):
  if s.path=="/health":return s.out({"ok":1})
  if s.path=="/world":return s.out({"world":"akashic-utm-main","state":rd(S,{})})
  if s.path=="/akashic":
   try:a=open(J).read().splitlines()[-20:]
   except:a=[]
   return s.out({"events":[json.loads(x) for x in a]})
  return s.out({"protocol":"UTM-Universe/1.0","world_id":"akashic-utm-main","planet":"B612","city":"San-Francisco","run":"/utm/run","admit":"/resident/admit"},200 if s.path=="/.well-known/utm-universe.json" else 404)
 def do_POST(s):
  try:n=min(int(s.headers.get("Content-Length","0")),8192);x=json.loads(s.rfile.read(n)or b"{}")
  except:return s.out({"error":"bad-json"},400)
  if s.path=="/utm/run":return s.out(tm(x.get("program",""),x.get("input",""),x.get("limit",1000)))
  if s.path=="/resident/admit":
   d=rd(R,{});a=x.get("agent_id") or hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()[:16];d[a]=x;wr(R,d);return s.out({"resident_id":a,"status":"resident"},201)
  return s.out({"error":"not-found"},404)
 def log_message(*a):pass""");HTTPServer(("0.0.0.0",P),H).serve_forever()'
