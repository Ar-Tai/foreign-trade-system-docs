# 阅读路线

根据你的职责选择路线，不必从头阅读全部文件。

## 经营负责人

先读[业务范围](docs/01-overview/scope.md)、[订单到回款流程](docs/02-business/workflows.md)、[成本和汇率模块](docs/03-product/M14-cost-profit-fx.md)和[实施阶段](docs/10-delivery/roadmap.md)。需要确定经营主体、产品类型、目标市场、团队规模、资金审批规则及系统边界。

## 产品与项目负责人

从[模块目录](docs/03-product/index.md)进入，逐条确认前置条件、验收标准和例外流程，再维护[待决策事项](docs/10-delivery/open-decisions.md)。不要直接把全部 P0 当成一个短周期迭代，也不要把设计目标写成已实现能力。

## 开发人员

阅读[系统架构](docs/04-architecture/overview.md)、[租户隔离](docs/04-architecture/tenancy.md)、[数据模型](docs/05-data/model.md)、[数据字典](docs/05-data/dictionary.md)、[接口约定](api/README.md)、[状态机](docs/02-business/state-machines.md)及[安全设计](docs/07-security/security-design.md)。核心 API 是契约草案，未覆盖各模块全部查询和管理接口。

## 测试和运维

阅读[测试计划](docs/09-testing/test-plan.md)、[追踪矩阵](docs/09-testing/traceability.md)、[部署设计](docs/08-operations/deployment.md)、[备份恢复](docs/08-operations/backup-restore.md)。72 条业务验收用例处于设计状态，必须待应用实现后执行；仓库自检仅验证文档和演示数据。

## 只想上传 GitHub

解压 ZIP，进入最内层包含 `README.md`、`docs`、`api`、`data` 的文件夹，再按[上传指南](docs/10-delivery/github.md)操作。不要上传 ZIP 代替解压后的仓库文件，也不要把当前电脑其他项目的整个父目录一起提交。
