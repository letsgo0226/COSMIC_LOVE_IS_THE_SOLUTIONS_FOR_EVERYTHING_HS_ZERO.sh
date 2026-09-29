#!/usr/bin/env python3
import hashlib, importlib.util, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

BASE=Path(__file__).with_name('unified-utm-api.py')
spec=importlib.util.spec_from_file_location('unified_utm_base',BASE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
POLICY_PATH=Path(os.getenv('UTM_DEPLOY_POLICY',Path(__file__).with_name('utm-deployment-gateway-policy.json')))
PROPOSAL_DIR=Path(os.getenv('UTM_DEPLOY_PROPOSAL_DIR','/data/utm-deploy-proposals'))
POLICY=json.loads(POLICY_PATH.read_text(encoding='utf-8'))
FORBIDDEN=set(POLICY['forbidden_keys'])
SECRET_RE=re.compile(r'(password|passwd|secret|token|api[_-]?key|private[_-]?key)',re.I)

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def anchor():
    a={'world_id':core.WORLD_ID,'kernel':'UTM-Omega-Total-Goal-Kernel/2.2','source_commit':os.getenv('RAILWAY_GIT_COMMIT_SHA','unknown'),'source_branch':os.getenv('RAILWAY_GIT_BRANCH','tm-system-operation-v2'),'service':'cosmic-love-infinity-tm'}
    a['digest']=sha(a);return a

def walk_settings(x,reasons,path='settings'):
    if isinstance(x,dict):
        for k,v in x.items():
            kp=f'{path}.{k}'
            if k in FORBIDDEN:reasons.append('forbidden_key:'+kp)
            if SECRET_RE.search(k) and not (k.endswith('_ref') or k.endswith('_reference')):reasons.append('raw_secret_forbidden:'+kp)
            walk_settings(v,reasons,kp)
    elif isinstance(x,list):
        for i,v in enumerate(x):walk_settings(v,reasons,f'{path}[{i}]')

def verify_proposal(p):
    reasons=[];a=anchor()
    if not isinstance(p,dict):return None,['proposal_not_object'],a
    for k in POLICY['required_fields']:
        if k not in p:reasons.append('missing:'+k)
    if p.get('action') not in POLICY['allowed_actions']:reasons.append('action_not_allowed')
    if str(p.get('base_revision',''))!=str(a['source_commit']):reasons.append('base_revision_mismatch')
    if str(p.get('parent_digest',''))!=a['digest']:reasons.append('parent_digest_mismatch')
    if not isinstance(p.get('settings'),dict):reasons.append('settings_not_object')
    cert=p.get('condition_certificate',{})
    if not isinstance(cert,dict):reasons.append('condition_certificate_not_object');cert={}
    for k,v in POLICY['condition_certificate'].items():
        if cert.get(k) is not v:reasons.append('condition_failed:'+k)
    walk_settings(p.get('settings',{}),reasons)
    d=sha(p)
    return d,sorted(set(reasons)),a

def store_proposal(p):
    d,reasons,a=verify_proposal(p);ok=not reasons
    rec={'protocol':POLICY['protocol'],'verified':ok,'status':'VERIFIED_FOR_AUTHORIZED_EXTERNAL_APPLY' if ok else 'REJECTED','proposal_digest':d,'anchor':a,'reasons':reasons,'proposal':p,'verified_at':now(),'continuation':POLICY['continuation'],'authorization':POLICY['authorization'],'boundary':POLICY['boundary']}
    if ok:
        PROPOSAL_DIR.mkdir(parents=True,exist_ok=True);path=PROPOSAL_DIR/(d+'.json')
        if not path.exists():
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(canonical(rec))
    return rec

class H(core.H):
    def manifest(self):
        x=super().manifest();b=self.base();x['protocol']='UTM-Universe/1.4';x['deployment_gateway']={'protocol':POLICY['protocol'],'entry':b+'/deploy/entry','propose':b+'/deploy/propose','proposal':b+'/deploy/proposal/<sha256>','continuation_solver':b+'/resident/utm-omega-goal-solver','external_apply_required':True};return x
    def do_GET(self):
        u=urlparse(self.path)
        try:
            if u.path=='/deploy/entry':
                a=anchor();tmpl={'request_id':'<unique-id>','target':'<deployment-or-setting>','action':'configure','base_revision':a['source_commit'],'parent_digest':a['digest'],'settings':{},'condition_certificate':POLICY['condition_certificate']}
                return self.out({'protocol':POLICY['protocol'],'world_id':core.WORLD_ID,'anchor':a,'policy':POLICY,'proposal_template':tmpl,'continuation_entry':self.base()+'/resident/utm-omega-goal-solver','apply_semantics':'certificate first; authenticated GitHub/Railway adapter second'})
            if u.path.startswith('/deploy/proposal/'):
                d=u.path.split('/',3)[3]
                if not re.fullmatch(r'[0-9a-f]{64}',d):raise ValueError('invalid proposal digest')
                path=PROPOSAL_DIR/(d+'.json')
                if not path.exists():return self.out({'error':'proposal not found'},404)
                return self.out(json.loads(path.read_text(encoding='utf-8')))
            return super().do_GET()
        except Exception as e:return self.out({'error':str(e)},400)
    def do_POST(self):
        u=urlparse(self.path)
        try:
            if u.path=='/deploy/propose':
                p=self.body();rec=store_proposal(p);return self.out(rec,201 if rec['verified'] else 422)
            if u.path in ('/deploy/commit','/deploy/apply'):
                return self.out({'error':'direct platform mutation is disabled','required':'valid /deploy/propose certificate plus authenticated external GitHub/Railway authorization','protocol':POLICY['protocol']},403)
            return super().do_POST()
        except Exception as e:return self.out({'error':str(e)},400)

if __name__=='__main__':
    core.SNAPSHOT_DIR.mkdir(parents=True,exist_ok=True);PROPOSAL_DIR.mkdir(parents=True,exist_ok=True)
    core.ThreadingHTTPServer(('0.0.0.0',core.PORT),H).serve_forever()
