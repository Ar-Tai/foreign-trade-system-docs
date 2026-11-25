# 数据字典与字段规范

这是逻辑模型，不是可直接执行的数据库迁移。实际 DDL、索引、约束、金额精度和数据库产品需经实施评审。

## 公共字段

| 字段 | 建议逻辑类型 | 约束 |
| --- | --- | --- |
| id | UUID | 服务端生成且不可变 |
| tenant_id | UUID | 必填 来自已验证上下文 |
| version | 正整数 | 初始为 1 关键写操作递增 |
| created_at updated_at | UTC 时间点 | 保存时区明确的时间 |
| created_by updated_by | 用户标识 | 系统任务也要有可追踪主体 |
| status | 有限枚举 | 只能经允许的状态迁移更新 |
| currency | 三位币种代码 | 采用租户允许且已配置精度的币种 |
| quantity | 精确十进制 | 不使用 float 关键业务校验正负与单位 |
| amount | 精确十进制 | 同时保存币种 金额与币种不能拆分使用 |
| source_reference | 来源标识 | 外部映射须包含连接与租户 |
| revision | 版本标识 | 对外业务快照不可原地覆盖 |

API 中精确数字序列化为字符串，以避免客户端浮点误差。数据库可采用足够精度的 DECIMAL 或 NUMERIC，具体上限由商品单位和财务规模决定，不允许隐式截断。

## 业务实体

| 实体组 | 核心字段或关系 | 必需约束 |
| --- | --- | --- |
| Tenant Membership | 租户 成员 用户 状态 | 同租户同用户关系唯一 |
| Role Permission | 动作 数据范围 授权来源 | 默认拒绝 职责分离 |
| Category | code parent_id name | 编码唯一 父子层级无环 |
| Product SKU | code category_id revision attributes | 租户内SKU唯一 |
| Supplier Qualification | 法律名称 能力 资料 有效期 | 过期资料不得当作有效 |
| SupplierBankRevision | 受益人账户版本 审核链 | 付款引用已批准版本 |
| Customer Contact | 公司 联系人 归属 地址 | 联系人与公司分别授权 |
| Inquiry Opportunity | 来源 需求版本 下次行动 | 外部编号幂等 |
| Quotation QuotationLine | 规格 数量 单价 条款 有效期 | 明细总额可重算 |
| SampleOrder | 规格 样品费 运输 结论 | 关联需求及报价版本 |
| SalesOrder SalesOrderLine | 合同快照 有效数量 三条状态轴 | 接受报价转换唯一 |
| OrderAmendment | 原版本 新内容 审批 生效时间 | 未批准不得影响履约 |
| PurchaseOrder PurchaseOrderLine | 供应商 数量 成本 承诺日期 | 已收量不超过有效采购量 |
| ProcurementAllocation | 销售行 采购行 分配数量 | 两边分配不超额 |
| Inspection QualityHold | 批次 方案 数据 结果 处置 | 不合格记录不可覆盖 |
| Warehouse StockLot | 货位 SKU 批次 到期日 | 仓库及批次归属一致 |
| InventoryBalance | on_hand reserved blocked | 分区非负 合计不超在手 |
| StockMovement | 来源 类型 数量 前后余额 | 业务来源操作唯一 |
| Reservation | 订单行 库存桶 数量 有效状态 | 有效预留受库存约束 |
| Shipment ShipmentLine | 出运 订单行 数量 运输信息 | 有效出运量不超订单 |
| Package PackageLine | 箱号 出运行 数量 重量 | 箱内与出运汇总一致 |
| TradeDocument Revision | 类型 数据快照 模板版本 文件哈希 | 已签发文件不可覆盖 |
| ClassificationRecord | 辖区 编码版本 依据 审核人 | 内部类目不得替代归类 |
| Receivable Payable | 对手方 单据 币种 金额 到期日 | 余额可由调整和核销推导 |
| Payment Allocation | 原始金额 净额 费用 分配对象 | 并发不超款项及账单余额 |
| CostEntry Allocation | 原币 成本分类 分摊及汇率 | 分摊合计守恒 |
| Claim ReturnReceipt | 原出运 批次 数量 处置 | 退货先隔离后放行 |
| ApprovalInstance Decision | 资源版本 规则版本 审批记录 | 变更后旧批准失效 |
| Attachment | 大小 类型 哈希 扫描 归属 | 通过检查后才可下载 |
| AuditEvent | 主体 动作 资源 结果 请求编号 | 追加写 防止业务角色篡改 |
| Inbox Outbox | 事件ID 摘要 状态 重试 | 接收与处理分别记录 |
