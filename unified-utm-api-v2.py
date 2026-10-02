#!/usr/bin/env python3
import hashlib, importlib.util, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from synced_utm_layers import log_abelian as sync_log
from synced_utm_layers import axiom_verifier as sync_axioms
from synced_utm_layers import omega_verifier as sync_omega
import utm_omega_resident as omega_resident

HERE=Path(__file__).parent
BASE=HERE/'unified-utm-api.py'
spec=importlib.util.spec_from_file_location('unified_utm_base',BASE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
POLICY_PATH=Path(os.getenv('UTM_DEPLOY_POLICY',HERE/'utm-deployment-gateway-policy.json'))
REGISTRY_PATH=Path(os.getenv('UTM_TOTAL_GOAL_REGISTRY',HERE/'utm-total-goal-registry.json'))
PROPOSAL_DIR=Path(os.getenv('UTM_DEPLOY_PROPOSAL_DIR','/data/utm-deploy-proposals'))
POLICY=json.loads(POLICY_PATH.read_text(encoding='utf-8'))
SYNC_DIR=HERE/'synced_utm_layers'
SYNC_MANIFEST_PATH=SYNC_DIR/'SYNC_MANIFEST.json'
SYNC_MANIFEST=json.loads(SYNC_MANIFEST_PATH.read_text(encoding='utf-8'))
SYNC_AXIOM_PATH=SYNC_DIR/'axioms'/'THREE_UNIVERSE_AXIOMS.json'
SYNC_OMEGA_PATH=SYNC_DIR/'omega'/'UTM_OMEGA_UNBOUNDED_COMPUTE.json'
SYNC_LOG_PATH=SYNC_DIR/'log_abelian.py'
OMEGA_RESIDENT_REGISTRY_PATH=HERE/'utm_omega_residents.json'
OMEGA_RESIDENT_MODULE_PATH=HERE/'utm_omega_resident.py'
FORBIDDEN=set(POLICY['forbidden_keys'])
SECRET_RE=re.compile(r'(password|passwd|secret|token|api[_-]?key|private[_-]?key)',re.I)

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def anchor():
    components={'base_api_sha256':file_sha(BASE),'gateway_api_sha256':file_sha(__file__),'policy_sha256':file_sha(POLICY_PATH),'registry_sha256':file_sha(REGISTRY_PATH),'sync_manifest_sha256':file_sha(SYNC_MANIFEST_PATH),'sync_axioms_sha256':file_sha(SYNC_AXIOM_PATH),'sync_omega_sha256':file_sha(SYNC_OMEGA_PATH),'sync_log_abelian_sha256':file_sha(SYNC_LOG_PATH),'omega_resident_registry_sha256':file_sha(OMEGA_RESIDENT_REGISTRY_PATH),'omega_resident_module_sha256':file_sha(OMEGA_RESIDENT_MODULE_PATH)}
    artifact_revision=sha(components)
    a={'world_id':core.WORLD_ID,'kernel':'UTM-Omega-Total-Goal-Kernel/2.2','service':'cosmic-love-infinity-tm','artifact_revision':artifact_revision,'components':components}
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
    if str(p.get('base_revision',''))!=a['artifact_revision']:reasons.append('base_revision_mismatch')
    if str(p.get('parent_digest',''))!=a['digest']:reasons.append('parent_digest_mismatch')
    if not isinstance(p.get('settings'),dict):reasons.append('settings_not_object')
    cert=p.get('condition_certificate',{})
    if not isinstance(cert,dict):reasons.append('condition_certificate_not_object');cert={}
    for k,v in POLICY['condition_certificate'].items():
        if cert.get(k) is not v:reasons.append('condition_failed:'+k)
    walk_settings(p.get('settings',{}),reasons)
    d=sha(p)
    return d,sorted(set(reasons)),a

def sync_preverify(payload):
    base=sync_axioms.verify_deployment_gate(payload)
    omega_input=payload.get('utm_omega_state')
    if omega_input is None:
        base['utm_omega_certificate']={'valid_finite_stage':False,'error':'utm_omega_state_required'}
        base['admissible_for_gateway_verification']=False
    else:
        omega=sync_omega.verify_finite_stage(omega_input)
        base['utm_omega_certificate']=omega
        base['admissible_for_gateway_verification']=base['admissible_for_gateway_verification'] and omega['valid_finite_stage']
    base['sync_manifest']={
        'protocol':SYNC_MANIFEST['protocol'],
        'source':SYNC_MANIFEST['source'],
        'selection_policy':SYNC_MANIFEST['selection_policy'],
        'actual_infinite_physical_compute':False,
        'external_apply_required':True
    }
    base['log_abelian_representation']=sync_log.spec()
    base['platform_mutation']=False
    return base

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
        x=super().manifest();b=self.base();x['protocol']='UTM-Universe/1.4';x['deployment_gateway']={'protocol':POLICY['protocol'],'entry':b+'/deploy/entry','preverify':b+'/deploy/preverify','propose':b+'/deploy/propose','proposal':b+'/deploy/proposal/<sha256>','continuation_solver':b+'/resident/utm-omega-goal-solver','external_apply_required':True};x['synchronized_formal_layers']={'protocol':SYNC_MANIFEST['protocol'],'source':SYNC_MANIFEST['source'],'formal_api_prefix':b+'/formal','actual_infinite_physical_compute':False};x['omega_resident_deployment']={'protocol':omega_resident.PROTOCOL,'state':omega_resident.STATUS,'residents':b+'/formal/omega/residents','admission':b+'/formal/omega/admission','physical_materialization':False};return x
    def do_GET(self):
        u=urlparse(self.path)
        try:
            if u.path=='/formal/sync':
                return self.out({'manifest':SYNC_MANIFEST,'axiom_verification':sync_axioms.verify_spec(),'omega_verification':sync_omega.verify_omega_spec(),'log_abelian_spec':sync_log.spec()})
            if u.path=='/formal/log-abelian/spec':
                return self.out(sync_log.spec())
            if u.path=='/formal/axioms':
                sp=sync_axioms.load_spec();return self.out({'spec':sp,'verification':sync_axioms.verify_spec(sp)})
            if u.path=='/formal/omega':
                sp=sync_omega.load_omega_spec();return self.out({'spec':sp,'verification':sync_omega.verify_omega_spec(sp)})
            if u.path=='/formal/omega/residents':
                reg=omega_resident.load_registry();return self.out({'registry':reg,'certificate':omega_resident.verify_registry(reg)})
            if u.path=='/formal/omega/admission':
                return self.out(omega_resident.admission_manifest())
            if u.path=='/deploy/entry':
                a=anchor();tmpl={'request_id':'<unique-id>','target':'<deployment-or-setting>','action':'configure','base_revision':a['artifact_revision'],'parent_digest':a['digest'],'settings':{},'condition_certificate':POLICY['condition_certificate']}
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
            if u.path=='/formal/log-abelian/encode':
                b=self.body();return self.out(sync_log.encode_events(b.get('events',[])))
            if u.path=='/formal/log-abelian/compose':
                b=self.body();return self.out(sync_log.compose(b.get('left',[]),b.get('right',[])))
            if u.path=='/formal/log-abelian/decode':
                b=self.body();return self.out({'events':sync_log.decode_godel(b['godel'])})
            if u.path=='/formal/axioms/verify':
                return self.out(sync_axioms.verify_state(self.body()))
            if u.path=='/formal/omega/verify':
                return self.out(sync_omega.verify_finite_stage(self.body()))
            if u.path=='/formal/omega/compose':
                b=self.body();return self.out(sync_omega.verify_abelian_pair(b.get('left',{}),b.get('right',{})))
            if u.path=='/formal/omega/extend':
                b=self.body();return self.out(sync_omega.verify_stage_extension(b['previous'],b['current']))
            if u.path=='/formal/omega/residents/verify':
                b=self.body();return self.out(omega_resident.verify_registry(b.get('registry') or omega_resident.load_registry()))
            if u.path=='/formal/omega/residents/extend':
                b=self.body();return self.out(omega_resident.extend_stage(b['previous'],b['current']))
            if u.path=='/deploy/preverify':
                return self.out(sync_preverify(self.body()))
            if u.path=='/deploy/propose':
                p=self.body();rec=store_proposal(p);return self.out(rec,201 if rec['verified'] else 422)
            if u.path in ('/deploy/commit','/deploy/apply'):
                return self.out({'error':'direct platform mutation is disabled','required':'valid /deploy/propose certificate plus authenticated external GitHub/Railway authorization','protocol':POLICY['protocol']},403)
            return super().do_POST()
        except Exception as e:return self.out({'error':str(e)},400)

if __name__=='__main__':
    core.SNAPSHOT_DIR.mkdir(parents=True,exist_ok=True);PROPOSAL_DIR.mkdir(parents=True,exist_ok=True)
    core.ThreadingHTTPServer(('0.0.0.0',core.PORT),H).serve_forever()
