#!/usr/bin/env python3
import json,os,http.client
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse
PORT=int(os.getenv("PORT","8080"));UPSTREAM_PORT=int(os.getenv("UTM_UPSTREAM_PORT","8081"));LATEST=Path("/app/utm-singularity/latest.json")
class H(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def reply(self,obj,code=200):
        b=json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode();self.send_response(code);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def proxy(self):
        n=int(self.headers.get("Content-Length","0") or 0);body=self.rfile.read(n) if n else None;c=http.client.HTTPConnection("127.0.0.1",UPSTREAM_PORT,timeout=30);h={k:v for k,v in self.headers.items() if k.lower() not in ("host","content-length")};c.request(self.command,self.path,body=body,headers=h);r=c.getresponse();b=r.read();self.send_response(r.status)
        for k,v in r.getheaders():
            if k.lower() not in ("transfer-encoding","connection","content-length"):self.send_header(k,v)
        self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b);c.close()
    def do_GET(self):
        if urlparse(self.path).path=="/omega/snapshot":
            try:
                x=json.loads(LATEST.read_text());x["permanent_address"]=f"{self.headers.get('X-Forwarded-Proto','https')}://{self.headers.get('Host','')}/omega/snapshot";return self.reply(x)
            except Exception as e:return self.reply({"error":str(e)},500)
        return self.proxy()
    def do_POST(self):return self.proxy()
if __name__=="__main__":ThreadingHTTPServer(("0.0.0.0",PORT),H).serve_forever()
