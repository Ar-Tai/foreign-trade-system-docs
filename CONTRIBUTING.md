# 文档协作规范

## 变更入口

业务范围、规则和架构直接编辑 `docs` 内对应 Markdown。模块与验收条目的权威源为 [module-specs.json](data/module-specs.json)，品类源为 [catalog.json](data/catalog.json)。修改这些源文件后运行：

```bash
python scripts/build_reference.py
python scripts/check_docs.py
python -m unittest discover -s tests -v
```

生成文件包含模块规格、模块索引、追踪矩阵、品类阅读版及需求与测试 JSON。不要只改生成文件；`--check` 会发现未同步内容。需求编号和模块编号应保持稳定，不用重新排序来复用旧编号。

接口契约以 `api/openapi.json` 为源，`schemas/api-models.schema.json` 是生成的 Schema 镜像；修改接口后同样运行生成与校验命令。

## PR 要求

写清业务原因、影响的需求、数据字段、接口及测试。涉及金额、库存、租户隔离和审批的变更至少由相应业务或安全负责人复核。禁止将真实客户数据、密钥、合同、银行资料及未经授权的第三方全文加入仓库。

## 来源与状态

新事实保留官方来源和核对日期，假设与设计目标明确标注。用例在没有执行证据前维持 designed；文档维护不能把业务测试状态批量改成 passed。对外发布与许可证选择由仓库所有者决定。
