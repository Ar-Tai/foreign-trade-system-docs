"""Repository validation only. No live trading service is contacted or tested."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
EXCLUDE={'.git','.venv','__pycache__','.checks','dist'}

def files(root):
    return sorted(p for p in root.rglob('*') if p.is_file() and not any(x in EXCLUDE for x in p.relative_to(root).parts))

def inventory_valid(bucket):
    values=[Decimal(bucket[k]) for k in ('on_hand','reserved','blocked')]
    if not all(x.is_finite() and x >= 0 for x in values):return False
    hand,reserved,blocked=values
    return reserved+blocked <= hand

def allocation_valid(payment_remaining,invoice_remaining,amount):
    """Pure design arithmetic; does NOT implement locking, authorization or a ledger."""
    p,i,a=map(Decimal,(payment_remaining,invoice_remaining,amount))
    return all(x.is_finite() for x in (p,i,a)) and p>=0 and i>=0 and 0<a<=min(p,i)

def verify_demo(d):
    D=Decimal
    quant=D(1).scaleb(-d['currency_scale'])
    rounding=lambda n:n.quantize(quant,rounding=ROUND_HALF_UP)
    quantity=D(d['quantity'])
    assert quantity>0
    total=rounding(quantity*D(d['unit_price'])-D(d['line_discount']))+D(d['freight_revenue'])
    assert total==D(d['order_total']), 'order total mismatch'
    assert sum((D(p['gross']) for p in d['payments']),D(0))==total, 'payment total mismatch'
    for p in d['payments']:
        assert D(p['bank_net'])+D(p['fee'])==D(p['gross']), 'bank gross/net mismatch'
    shipped=sum((D(q) for q in d['shipments']),D(0))
    assert all(D(q)>0 for q in d['shipments']) and shipped==quantity, 'shipment quantity mismatch'
    fx=d['fx']; rate=D(fx['rate'])
    assert rate>0 and fx['base_currency']==d['currency'], 'unsupported fixture FX direction'
    cost=D(0)
    for c in d['costs']:
        value=D(c['amount'])
        assert value>=0
        if c['currency']==d['currency']:cost+=value
        else:
            assert c['currency']==fx['quote_currency'], 'missing FX rate'
            cost+=rounding(value/rate)
    assert cost==D(d['expected_total_cost']), 'cost mismatch'
    assert total-cost==D(d['expected_contribution']), 'contribution mismatch'
    fees=sum((D(p['fee']) for p in d['payments']),D(0))
    fee_cost=sum((D(c['amount']) for c in d['costs'] if c['type']=='bank_fees' and c['currency']==d['currency']),D(0))
    assert fees==fee_cost, 'fee accounting mismatch'
    inv=d['inventory']
    current={'on_hand':inv['initial_on_hand'],'reserved':inv['reserved'],'blocked':inv['blocked']}
    assert inventory_valid(current), 'invalid initial inventory'
    for q,key in zip(d['shipments'],('after_first_dispatch','after_second_dispatch'),strict=True):
        current={**current,'on_hand':str(D(current['on_hand'])-D(q)),'reserved':str(D(current['reserved'])-D(q))}
        assert inventory_valid(current) and all(D(current[k])==D(inv[key][k]) for k in current),'inventory dispatch mismatch'
    return {'order_total':str(total),'total_cost':str(cost),'contribution':str(total-cost),'shipped_quantity':str(shipped)}

def check_links(root):
    checked=0
    exact={p.relative_to(root).as_posix() for p in files(root)}
    for path in files(root):
        if path.suffix!='.md':continue
        text=path.read_text(encoding='utf-8')
        assert text.count('```')%2==0, f'unclosed code fence: {path.name}'
        visible=re.sub(r'```.*?```','',text,flags=re.S)
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)',visible):
            parsed=urlsplit(target)
            if parsed.scheme or target.startswith('#'):continue
            local=(path.parent/unquote(parsed.path)).resolve()
            assert local.is_relative_to(root.resolve()), f'link escapes repository: {target}'
            rel=local.relative_to(root.resolve()).as_posix()
            assert local.is_file() and rel in exact, f'broken or case-mismatched link: {path.relative_to(root)} -> {target}'
            checked+=1
    return checked

def check_catalog(c):
    ids=[];subids=[];mentions=0
    for cat in c['categories']:
        ids.append(cat['id'])
        for sub in cat['children']:
            assert sub['id'].startswith(cat['id']+'.'), 'wrong category parent'
            subids.append(sub['id'])
            assert sub['name'] and all(x.strip() for x in sub['examples'])
            mentions+=len(sub['examples'])
    assert len(ids)==len(set(ids)) and len(subids)==len(set(subids)), 'duplicate category code'
    actual={'primary':len(ids),'secondary':len(subids),'example_mentions':mentions}
    assert actual==c['counts'], 'catalog counts differ'
    assert actual=={'primary':80,'secondary':640,'example_mentions':3840}, 'baseline changed: review counts and claims'
    return actual

def check_trace(root):
    req=json.loads((root/'data/requirements.json').read_text(encoding='utf-8'))['requirements']
    tests=json.loads((root/'data/acceptance-tests.json').read_text(encoding='utf-8'))['tests']
    assert len(req)==len(tests)==72
    assert len({r['id'] for r in req})==72 and len({t['id'] for t in tests})==72
    test_map={t['id']:t for t in tests}
    for r in req:
        t=test_map[r['test_id']]
        assert t['requirement_id']==r['id'] and t['module_id']==r['module_id']
        assert t['expected_result']==r['acceptance']
        assert t['status']=='designed' and t['actual_result'] is None
        assert (root/r['spec_path']).is_file()
    return len(req)

def validate_all(root=ROOT):
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
    from openapi_spec_validator import validate
    from scripts.build_reference import generate
    allfiles=files(root)
    assert all(p.stat().st_size < 10*1024*1024 for p in allfiles), 'unexpected large repository file'
    badnames={'.env','secrets.json','ACCESS.txt'}
    secret=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    for p in allfiles:
        assert p.name not in badnames, f'private filename: {p.name}'
        if p.suffix in {'.md','.json','.py','.yml','.txt'}:
            s=p.read_text(encoding='utf-8')
            assert not secret.search(s), f'possible credential: {p.relative_to(root)}'
            assert not re.search(r'[A-Za-z]:[\\/]Users[\\/]',s), f'local personal path: {p.relative_to(root)}'
        if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8'))
        if p.suffix in {'.yml','.yaml'}:yaml.load(p.read_text(encoding='utf-8'),Loader=yaml.BaseLoader)
    for name,text in generate(root).items():
        assert (root/name).read_text(encoding='utf-8')==text, f'stale generated document: {name}'
    link_count=check_links(root)
    catalog=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
    counts=check_catalog(catalog)
    trace_count=check_trace(root)
    schemas={p.name:json.loads(p.read_text(encoding='utf-8')) for p in (root/'schemas').glob('*.json')}
    for schema in schemas.values():Draft202012Validator.check_schema(schema)
    checker=FormatChecker()
    Draft202012Validator(schemas['catalog.schema.json'],format_checker=checker).validate(catalog)
    demo=json.loads((root/'examples/demo-order.json').read_text(encoding='utf-8'))
    Draft202012Validator(schemas['demo-order.schema.json'],format_checker=checker).validate(demo)
    demo_result=verify_demo(demo)
    spec=json.loads((root/'api/openapi.json').read_text(encoding='utf-8'))
    validate(spec)
    operations={op['operationId']:op for item in spec['paths'].values() for method,op in item.items() if method in {'get','post','put','patch','delete'}}
    assert len(operations)==sum(len(i) for i in spec['paths'].values()),'duplicate operationId'
    for path,item in spec['paths'].items():
        for method,op in item.items():
            if method!='get' and not path.startswith('/integrations/'):
                assert any(p.get('$ref')=='#/components/parameters/IdempotencyKey' for p in op['parameters'])
    examples=json.loads((root/'examples/api-requests.json').read_text(encoding='utf-8'))['requests']
    api_schema=schemas['api-models.schema.json']
    for entry in examples:
        op=operations[entry['operation_id']]
        target=op['requestBody']['content']['application/json']['schema']['$ref'].split('/')[-1]
        validator=Draft202012Validator({**api_schema,'$ref':f'#/$defs/{target}'},format_checker=checker)
        validator.validate(entry['body'])
    machines=json.loads((root/'data/state-machines.json').read_text(encoding='utf-8'))['machines']
    for name,m in machines.items():
        assert m['initial'] in m['states'] and len(m['states'])==len(set(m['states']))
        keys=set()
        for source,action,target,guard in m['transitions']:
            assert source in m['states'] and target in m['states'] and guard
            assert (source,action) not in keys
            keys.add((source,action))
    workflow_path=root/'.github/workflows/docs-check.yml'
    workflow_enabled=workflow_path.exists()
    if not workflow_enabled:
        workflow_path=root/'templates/docs-check.github-actions.yml'
    workflow=yaml.load(workflow_path.read_text(encoding='utf-8'),Loader=yaml.BaseLoader)
    assert workflow['permissions']=={'contents':'read'}
    assert {'push','pull_request','workflow_dispatch'}<=set(workflow['on'])
    assert 'pull_request_target' not in workflow['on']
    for step in workflow['jobs']['validate']['steps']:
        if 'uses' in step:assert re.search(r'@[a-f0-9]{40}$',step['uses'])
    with ZipFile(root/'references/category-handbook.docx') as z:
        assert z.testzip() is None
        for name in ('word/document.xml','docProps/core.xml'):
            text=z.read(name).decode('utf-8')
            assert not re.search(r'[A-Za-z]:[\\/]Users[\\/]',text)
    manifest=root/'MANIFEST.sha256'
    if manifest.exists():
        for line in manifest.read_text(encoding='utf-8').splitlines():
            digest,path=line.split('  ',1)
            assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest, f'manifest mismatch: {path}'
    return {'status':'passed','scope':'documentation_only_not_application_acceptance','files_checked':len(allfiles),'markdown_files':sum(p.suffix=='.md' for p in allfiles),'internal_links_checked':link_count,'catalog':counts,'modules':18,'requirements':trace_count,'business_acceptance_tests':{'count':trace_count,'status':'designed_not_executed'},'openapi_operations':len(operations),'json_schemas':len(schemas),'api_request_examples_validated':len(examples),'state_machines':len(machines),'demo_arithmetic':demo_result,'github_remote_ci':'not_checked_by_local_validator' if workflow_enabled else 'not_enabled_reference_only','external_services':'not_connected','secret_scan':'limited_patterns_not_a_guarantee'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    result=validate_all()
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
