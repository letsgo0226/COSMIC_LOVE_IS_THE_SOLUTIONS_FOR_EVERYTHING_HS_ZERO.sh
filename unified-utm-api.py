#!/usr/bin/env python3
import base64, hashlib, html, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen

WORLD_ID=os.getenv("WORLD_ID","akashic-utm-main")
PLANET_ID=os.getenv("PLANET_ID","B612")
REGION_ID=os.getenv("REGION_ID","San-Francisco")
STATE=Path(os.getenv("LOG_TM_STATE","/data/cosmic-love-state.json"))
JOURNAL=Path(os.getenv("TM_OPERATION_JOURNAL","/data/cosmic-love-operations.jsonl"))
RESIDENTS=Path(os.getenv("RESIDENT_PATH","/data/residents.json"))
SNAPSHOT_DIR=Path(os.getenv("SNAPSHOT_DIR","/data/utm-address-snapshots"))
PORT=int(os.getenv("PORT","8080")); MAX_STEPS=int(os.getenv("TM_API_MAX_STEPS","2000")); MAX_BODY=65536; MAXQ=512
SEARCH_OMEGA_PROTOCOL="UTM-Universe/Search-Omega/1"

def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def rd(path,default):
    try:return json.loads(path.read_text())
    except:return json.loads(canonical(default))
def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(canonical(obj));os.replace(tmp,path)
def enc(s):
    n=1
    for b in s.encode("utf-8"):n=n*257+b+1
    return str(n)
def dec(g):
    n=int(g);a=[]
    if n<1:raise ValueError("invalid address")
    while n>1:
        n,r=divmod(n,257)
        if not 1<=r<=256:raise ValueError("invalid address")
        a.append(r-1)
    return bytes(a[::-1]).decode("utf-8")
def encx(s):
    n=1
    for b in s.encode("utf-8"):n=n*257+b+1
    return "0x"+format(n,"x")
def decx(g):
    if not isinstance(g,str) or not g.startswith("0x"):raise ValueError("invalid omega address")
    n=int(g,16);a=[]
    if n<1:raise ValueError("invalid omega address")
    while n>1:
        n,r=divmod(n,257)
        if not 1<=r<=256:raise ValueError("invalid omega address")
        a.append(r-1)
    return bytes(a[::-1]).decode("utf-8")
def canon(kind,value):
    if kind=="text":
        if not isinstance(value,str):raise ValueError("text value must be string")
        return "t:"+value
    if kind=="json":return "j:"+canonical(value)
    if kind=="bytes":
        if not isinstance(value,str):raise ValueError("bytes value must be base64 string")
        raw=base64.b64decode(value,validate=True);return "b:"+base64.b64encode(raw).decode("ascii")
    raise ValueError("type must be text, json, or bytes")
def uncanon(c):
    if len(c)<2 or c[1] != ":":raise ValueError("invalid canonical object")
    k,v=c[0],c[2:]
    if k=="t":return "text",v
    if k=="j":return "json",json.loads(v)
    if k=="b":base64.b64decode(v,validate=True);return "bytes",v
    raise ValueError("invalid canonical object")
def object_record(g):
    c=dec(g);kind,value=uncanon(c);return {"GOBJECT":str(g),"type":kind,"value":value,"canonical":c}
def tm(program,input_text="",limit=1000):
    rules={}
    for raw in program.split(";"):
        if not raw.strip():continue
        a=raw.split(",")
        if len(a)!=5:raise ValueError("each transition must be q,read,next,write,L|R")
        q,r,nq,w,d=a
        if d not in ("L","R"):raise ValueError("direction must be L or R")
        rules[(q,r)]=(nq,w,d)
    q="0";h=t=0;T={i:c for i,c in enumerate(input_text) if c!="_"};limit=max(0,min(int(limit),MAX_STEPS))
    halted=False
    while t<limit:
        z=rules.get((q,T.get(h,"_")))
        if z is None:halted=True;break
        q,w,d=z
        if w=="_":T.pop(h,None)
        else:T[h]=w
        h+=1 if d=="R" else -1;t+=1
    A=list(T) or [0]
    return {"q":q,"h":h,"t":t,"halt":halted,"tape":"".join(T.get(k,"_") for k in range(min(A),max(A)+1)),"bounded":True,"step_limit":limit}
def search(q,site="",limit=8):
    z=("site:"+site+" " if site else "")+q
    raw=urlopen(Request("https://html.duckduckgo.com/html/?q="+quote_plus(z),headers={"User-Agent":"Mozilla/5.0"}),timeout=12).read().decode("utf8","ignore")
    out=[]
    for m in re.finditer(r'href="([^"]+)"',raw):
        u=html.unescape(m.group(1))
        if "uddg=" in u:u=parse_qs(urlparse(u).query).get("uddg",[u])[0]
        if not u.startswith("http") or (site and site not in u) or u in out:continue
        out.append(u)
        if len(out)>=limit:break
    return out
def omega_search(q,result,observed_at="",environment=None):
    if not isinstance(q,str) or not q or len(q)>MAXQ:raise ValueError("invalid query")
    if not isinstance(observed_at,str) or len(observed_at)>128:raise ValueError("invalid observed_at")
    if environment is None:environment={}
    payload={"protocol":SEARCH_OMEGA_PROTOCOL,"world":WORLD_ID,"substrate":"P_-1","query":q,"result":result,"observed_at":observed_at,"environment":environment}
    c=canonical(payload);gq=enc(q);go=encx(c)
    return {"protocol":SEARCH_OMEGA_PROTOCOL,"world":WORLD_ID,"substrate":"P_-1","query":q,"result":result,"observed_at":observed_at,"environment":environment,"GQUERY":gq,"GOMEGA":go,"encoding":"reversible-base257-integer/hex-serialization","hash_function":False,"omega":"P_Omega","actual_infinite_physical_compute":False}
def omega_decode(g):
    x=json.loads(decx(g))
    if x.get("protocol")!=SEARCH_OMEGA_PROTOCOL:raise ValueError("not a Search-Omega address")
    return x
def logos(states,i="I",p="P",q="Q"):
    S=[x.strip() for x in states.split(",") if x.strip()]
    if not S or any(not re.fullmatch(r"[01]{2}",x) for x in S):raise ValueError("states must be comma-separated PQ bits, e.g. 11,01")
    poss="11" in S;ctr="10" in S;valid=not ctr
    return {"model":"UTM_LOGOS_V1","I":i,"P":p,"Q":q,"states":S,"possible_I":poss,"counterpossible_P_and_not_Q":ctr,"valid_P_implies_Q":valid,"logos_consistent":poss and valid,"formula":"◇(P∧Q) ∧ ¬◇(P∧¬Q)","scope":"finite-declared-model","metaphysical_proof":False}
def omega(depth=8):
    n=max(1,min(int(depth),256));g0=enc("P_0")
    def row(k):
        g=enc("P_%+d"%k);m=abs(k)
        return {"k":k,"P":"P_%+d"%k,"G":g,"L":"log(%s/%s)"%(g,g0),"u":[1 if k>0 else -1,m],"projection":"P_-1","normalized_resource":[1,1]}
    return {"model":"BIDIRECTIONAL_OMEGA_COMPACTIFICATION_TM","depth":n,"substrate":{"name":"P_-1","projection":"pi(P_k)=P_-1","resource_invariant":"C_hat(P_k)=C0","physical_resource_creation":False},"godel_log":{"encoding":"reversible base-257 numbering of finite labels","G0":g0,"coordinate":"L(P_k)=log(G(P_k)/G0)","note":"log coordinate is symbolic; it does not create compute"},"expansion":{"law":"S_k=lambda^k*S_0","lambda":"constant > 1","normalized_resource":"C_app(P_k)/lambda^k=C0"},"branches":{"plus":[row(i) for i in range(1,n+1)],"minus":[row(-i) for i in range(1,n+1)]},"compactification":{"u":"sign(k)/abs(k)","plus_limit":"0+","minus_limit":"0-","identification":"0+ ~ 0- ~ Omega","omega":"P_Omega","topology":"one-point compactification of the two unbounded directions"},"potentially_unbounded_hierarchy":True,"actual_infinite_physical_compute":False,"scope":"formal UTM hierarchy and boundary certificate only; not evidence that the physical universe has infinite computation or that coordinate descriptions create independent hardware"}
def snapshot_path(gs):return SNAPSHOT_DIR/(gs+".json")
def make_snapshot(g,version,result):
    object_record(g);version=str(version)
    if not version or len(version)>128:raise ValueError("invalid version")
    gs=enc("snapshot:"+version+":"+str(g));path=snapshot_path(gs);SNAPSHOT_DIR.mkdir(parents=True,exist_ok=True)
    if path.exists():return rd(path,{})
    rec={"GSNAPSHOT":gs,"GOBJECT":str(g),"version":version,"result":result,"immutable_identity":True,"result_persistence":True}
    rec["sha256"]=hashlib.sha256(canonical(rec).encode()).hexdigest()
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as f:f.write(canonical(rec))
    except FileExistsError:return rd(path,{})
    return rec

class H(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def base(self):return f"{self.headers.get('X-Forwarded-Proto','https')}://{self.headers.get('Host','')}"
    def out(self,obj,code=200):
        b=json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode();self.send_response(code);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Access-Control-Allow-Headers","Content-Type");self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_OPTIONS(self):
        self.send_response(204);self.send_header("Access-Control-Allow-Origin","*");self.send_header("Access-Control-Allow-Headers","Content-Type");self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS");self.end_headers()
    def body(self):
        n=int(self.headers.get("Content-Length","0"))
        if n<1 or n>MAX_BODY:raise ValueError("invalid body length")
        return json.loads(self.rfile.read(n))
    def address(self,kind,value):
        c=canon(kind,value);g=enc(c);return {"type":kind,"value":value,"canonical":c,"GOBJECT":g,"utm_address":f"{self.base()}/object/{g}"}
    def manifest(self):
        b=self.base();return {"protocol":"UTM-Universe/1.3","world_id":WORLD_ID,"planet":PLANET_ID,"city":REGION_ID,"service":"consolidated-utm-runtime","search_omega_protocol":SEARCH_OMEGA_PROTOCOL,"endpoints":{"health":b+"/health","world":b+"/world","akashic":b+"/akashic","run":b+"/utm/run","admit":b+"/resident/admit","address":b+"/address","object":b+"/object/<GOBJECT>","snapshot":b+"/snapshot","search":b+"/search?q=<query>","search_omega_live":b+"/omega/search?q=<query>","search_omega_post":b+"/omega/search","search_omega_decode":b+"/omega/search/<GOMEGA>","logos":b+"/logos?states=11,01","omega":b+"/omega?depth=8"}}
    def decorate_omega(self,x):
        x=dict(x);x["query_address"]=f"{self.base()}/search/{x['GQUERY']}";x["omega_address"]=f"{self.base()}/omega/search/{x['GOMEGA']}";return x
    def do_GET(self):
        u=urlparse(self.path);p=parse_qs(u.query)
        try:
            if u.path in ("/","/.well-known/utm-universe.json","/manifest"):return self.out(self.manifest())
            if u.path=="/health":return self.out({"ok":1,"world_id":WORLD_ID,"planet":PLANET_ID,"city":REGION_ID,"runtime":"consolidated","protocol":"UTM-Universe/1.3"})
            if u.path=="/world":return self.out({"world":WORLD_ID,"planet":PLANET_ID,"city":REGION_ID,"state":rd(STATE,{})})
            if u.path=="/akashic":
                try:rows=[json.loads(x) for x in JOURNAL.read_text().splitlines()[-20:] if x.strip()]
                except:rows=[]
                return self.out({"events":rows})
            if u.path=="/address":
                kind=p.get("type",["text"])[0];raw=p.get("value",[""])[0];value=json.loads(raw) if kind=="json" else raw;return self.out(self.address(kind,value))
            if u.path.startswith("/object/") or u.path.startswith("/decode/"):
                g=u.path.split("/",2)[2];x=object_record(g);x["utm_address"]=f"{self.base()}/object/{g}";return self.out(x)
            if u.path.startswith("/snapshot/"):
                gs=u.path.split("/",2)[2];path=snapshot_path(gs)
                if not path.exists():return self.out({"error":"snapshot not found"},404)
                x=rd(path,{});x["snapshot_address"]=f"{self.base()}/snapshot/{gs}";return self.out(x)
            if u.path=="/logos":return self.out(logos(p.get("states",["11"])[0],p.get("i",["I"])[0],p.get("p",["P"])[0],p.get("q",["Q"])[0]))
            if u.path=="/omega":return self.out(omega(p.get("depth",["8"])[0]))
            if u.path=="/omega/search":
                q=p.get("q",[""])[0];site=p.get("site",[""])[0];limit=max(1,min(int(p.get("limit",["4"])[0]),6))
                r=search(q,site,limit);obs=datetime.now(timezone.utc).isoformat().replace("+00:00","Z");x=omega_search(q,r,obs,{"engine":"duckduckgo-html","site":site,"limit":limit,"mode":"live"});return self.out(self.decorate_omega(x))
            if u.path.startswith("/omega/search/"):
                g=u.path.split("/",3)[3];x=omega_decode(g);r=omega_search(x["query"],x.get("result"),x.get("observed_at",""),x.get("environment",{}));return self.out(self.decorate_omega(r))
            if u.path=="/search":q=p.get("q",[""])[0]
            elif u.path.startswith("/search/"):q=dec(u.path.split("/",2)[2])
            else:
                if u.path.startswith("/resident/"):
                    rid=u.path.split("/",2)[2];d=rd(RESIDENTS,{})
                    return self.out({"resident_id":rid,"capsule":d[rid]}) if rid in d else self.out({"error":"resident not found"},404)
                return self.out({"error":"not found"},404)
            if not q or len(q)>MAXQ:raise ValueError("invalid query")
            site=p.get("site",[""])[0];limit=max(1,min(int(p.get("limit",["8"])[0]),10));g=enc(q);go=enc(canon("text",q))
            return self.out({"query":q,"GQUERY":g,"GOBJECT":go,"utm_address":f"{self.base()}/search/{g}","object_address":f"{self.base()}/object/{go}","live":True,"results":search(q,site,limit)})
        except Exception as e:return self.out({"error":str(e)},400)
    def do_POST(self):
        try:
            u=urlparse(self.path);x=self.body()
            if u.path=="/address":
                if not isinstance(x,dict):raise ValueError("body must be JSON object")
                return self.out(self.address(x.get("type","json"),x.get("value")))
            if u.path=="/omega/search":
                if not isinstance(x,dict):raise ValueError("body must be JSON object")
                r=omega_search(x.get("query",""),x.get("result"),x.get("observed_at",""),x.get("environment",{}));return self.out(self.decorate_omega(r),201)
            if u.path=="/snapshot":
                r=make_snapshot(str(x.get("GOBJECT","")),x.get("version",""),x.get("result"));r=dict(r);r["snapshot_address"]=f"{self.base()}/snapshot/{r['GSNAPSHOT']}";return self.out(r,201)
            if u.path=="/utm/run":return self.out(tm(x.get("program",""),x.get("input",""),x.get("limit",1000)))
            if u.path=="/resident/admit":
                d=rd(RESIDENTS,{});rid=str(x.get("agent_id") or hashlib.sha256(canonical(x).encode()).hexdigest()[:16]);d[rid]=x;wr(RESIDENTS,d);return self.out({"resident_id":rid,"status":"resident"},201)
            return self.out({"error":"not found"},404)
        except Exception as e:return self.out({"error":str(e)},400)

if __name__=="__main__":
    SNAPSHOT_DIR.mkdir(parents=True,exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0",PORT),H).serve_forever()
