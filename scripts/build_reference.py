"""Generate readable references from tracked JSON; no network or business writes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def generate(root=ROOT):
    modules=json.loads((root/'data/module-specs.json').read_text(encoding='utf-8'))
    catalog=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
    outputs={}
    requirements=[]
    tests=[]
    index=['# 业务模块目录','','每个模块包含目的 角色 字段 流程 规则 需求及验收。P0和P1是设计优先级，不是实现状态。','', '| 模块 | 范围 | 优先级 | 需求数 |','| --- | --- | --- | --- |']
    for m in modules:
        path=f"docs/03-product/{m['id']}-{m['slug']}.md"
        index.append(f"| {m['id']} | [{m['title']}]({Path(path).name}) | {m['phase']} | {len(m['requirements'])} |")
        rows=[f"# {m['id']} {m['title']}",'',m['purpose'],'',f"优先级：{m['phase']}。角色：{m['roles']}。实现状态：设计。",'', '## 业务对象与字段','',f"对象：{m['entities']}。",'',f"关键字段：`{m['fields']}`。",'', '## 正常流程','',m['flow'],'','## 核心规则','']
        rows += [f'{i}. {rule}' for i,rule in enumerate(m['rules'],1)]
        rows += ['', '## 需求及验收','', '| 需求编号 | 需求 | 验收条件 |','| --- | --- | --- |']
        for i,(title,acceptance) in enumerate(m['requirements'],1):
            rid=f"REQ-{m['id']}-{i:02}"
            tid=f"TC-{m['id']}-{i:02}"
            rows.append(f'| {rid} | {title} | {acceptance} |')
            requirements.append({'id':rid,'module_id':m['id'],'title':title,'priority':m['phase'],'spec_path':path,'acceptance':acceptance,'test_id':tid,'implementation_status':'designed'})
            tests.append({'id':tid,'requirement_id':rid,'module_id':m['id'],'title':title,'status':'designed','preconditions':[f"为{m['roles']}建立限定权限的虚构测试账号。",f"准备{m['entities']}相关的最小有效及边界数据。","部署待测应用并记录构建版本；没有应用时不得将用例判为通过。"],'steps':[f'按模块正常流程准备触发“{title}”的业务对象。','执行验收条件描述的正常操作及相反或越界条件。','分别检查API、页面、数据库事实和审计事件，必要时并发或重试。'],'expected_result':acceptance,'evidence_required':['构建与环境','输入和关键步骤','断言结果','关联业务及审计编号'],'actual_result':None})
        rows += ['', '## 例外处理','',m['exceptions'],'','## 指标与核查','',m['metrics']+'。','', '[返回模块目录](index.md) · [对应验收矩阵](../09-testing/traceability.md)','']
        outputs[path]='\n'.join(rows)
    index += ['', '## 相关设计','', '- [交互与页面规范](ui-interactions.md)','- [业务流程](../02-business/workflows.md)','- [状态机](../02-business/state-machines.md)','- [接口覆盖范围](../../api/coverage.md)','']
    outputs['docs/03-product/index.md']='\n'.join(index)
    outputs['data/requirements.json']=json.dumps({'version':'0.1.0','requirements':requirements},ensure_ascii=False,indent=2)+'\n'
    outputs['data/acceptance-tests.json']=json.dumps({'version':'0.1.0','note':'业务用例设计 未执行','tests':tests},ensure_ascii=False,indent=2)+'\n'
    trace=['# 需求与验收追踪矩阵','','所有业务用例当前为 designed。下列映射可用于排期和验收；仓库单元测试不是这些业务用例的执行证据。','', '[结构化需求](../../data/requirements.json) · [结构化验收用例](../../data/acceptance-tests.json)','', '| 需求 | 模块 | 条目 | 测试 | 状态 |','| --- | --- | --- | --- | --- |']
    for r in requirements:
        trace.append(f"| {r['id']} | [{r['module_id']}](../03-product/{Path(r['spec_path']).name}) | {r['title']} | {r['test_id']} | designed |")
    outputs['docs/09-testing/traceability.md']='\n'.join(trace)+'\n'
    cat=['# 电商与外贸品类目录','','80个一级品类、640个二级细分、3840条产品和服务示例，示例含交叉归类，不是独立SKU总数。编号只用于业务检索，不是海关编码或经营许可。第71类为商品状态及模式索引，第73类为特殊属性索引。','', '[结构化数据](../../data/catalog.json) · [原有Word手册](../../references/category-handbook.docx)','','## 一级品类索引','']
    for c in catalog['categories']:
        cat.append(f"- {c['id']} {c['name']}")
    for c in catalog['categories']:
        cat += ['',f"## {c['id']} {c['name']}",'','业务形态：'+'、'.join(c['business_modes'])+'。'+c['note']+'。','', '| 编号 | 二级细分 | 产品或服务示例 |','| --- | --- | --- |']
        for s in c['children']:
            cat.append(f"| {s['id']} | {s['name']} | {'、'.join(s['examples'])} |")
    outputs['docs/05-data/catalog.md']='\n'.join(cat)+'\n'
    coverage=['# 核心接口覆盖清单','','这是契约覆盖表，不是实现清单。未列模块和命令仍需在开发前补齐接口设计。','', '| 方法 | 路径 | operationId | 描述 |','| --- | --- | --- | --- |']
    spec=json.loads((root/'api/openapi.json').read_text(encoding='utf-8'))
    def convert_refs(value):
        if isinstance(value,dict):
            return {k:(v.replace('#/components/schemas/','#/$defs/') if k=='$ref' else convert_refs(v)) for k,v in value.items()}
        if isinstance(value,list):return [convert_refs(x) for x in value]
        return value
    model_schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://example.com/schemas/api-models.schema.json','$defs':convert_refs(spec['components']['schemas'])}
    outputs['schemas/api-models.schema.json']=json.dumps(model_schema,ensure_ascii=False,indent=2)+'\n'
    for path,item in spec['paths'].items():
        for method,op in item.items():
            coverage.append(f"| {method.upper()} | `{path}` | `{op['operationId']}` | {op['summary']} |")
    coverage += ['', '## 尚需扩展','', '供应商及采购管理、生产节点、检验完整生命周期、收货调拨盘点、报价拒绝撤回、订单补充协议、退货退款、应付付款、报表、权限管理和完整门户接口均不包含在本核心契约中。上传申请也不等于完整附件服务；后续完成上传、扫描和授权下载需要补齐。','']
    outputs['api/coverage.md']='\n'.join(coverage)
    return outputs

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    outputs=generate()
    mismatches=[]
    for rel,content in outputs.items():
        p=ROOT/rel
        if args.check:
            if not p.exists() or p.read_text(encoding='utf-8')!=content:
                mismatches.append(rel)
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(content,encoding='utf-8',newline='\n')
    if mismatches:
        raise SystemExit('Generated files out of date: '+', '.join(mismatches))
    print(f'Generated reference files {"verified" if args.check else "written"}: {len(outputs)}')

if __name__=='__main__':main()
