# 核心接口覆盖清单

这是契约覆盖表，不是实现清单。未列模块和命令仍需在开发前补齐接口设计。

| 方法 | 路径 | operationId | 描述 |
| --- | --- | --- | --- |
| GET | `/categories` | `listCategorys` | 分页查询Category |
| GET | `/products` | `listProducts` | 分页查询Product |
| POST | `/products` | `createProduct` | 创建Product |
| GET | `/customers` | `listCustomers` | 分页查询Customer |
| POST | `/customers` | `createCustomer` | 创建Customer |
| GET | `/inquiries` | `listInquirys` | 分页查询Inquiry |
| POST | `/inquiries` | `createInquiry` | 创建Inquiry |
| POST | `/quotations` | `createQuotation` | 创建Quotation |
| GET | `/customers/{id}` | `getCustomer` | 客户详情 |
| POST | `/quotations/{id}/submit` | `submitQuotation` | 草稿提交审批 |
| POST | `/quotations/{id}/approve` | `approveQuotation` | 独立审批人批准当前版本 |
| POST | `/quotations/{id}/issue` | `issueQuotation` | 发出已批准报价 |
| POST | `/quotations/{id}/accept` | `acceptQuotation` | 有证据并在有效期内接受报价 |
| POST | `/sales-orders` | `createSalesOrder` | 从已接受报价创建订单 |
| GET | `/sales-orders/{id}` | `getSalesOrder` | 订单详情 |
| POST | `/sales-orders/{id}/confirm` | `confirmSalesOrder` | 审批授信及条款通过后确认 |
| GET | `/inventory/balances` | `listInventoryBalances` | 库存分区与可用量 |
| POST | `/inventory/reservations` | `createReservation` | 原子预留库存 |
| POST | `/shipments` | `createShipment` | 创建关联预留的出运草稿 |
| POST | `/shipments/{id}/ready` | `readyShipment` | 检查质检单证收款与库存放行 |
| POST | `/shipments/{id}/dispatch` | `dispatchShipment` | 原子出库并记录发运 |
| POST | `/receivables` | `createReceivable` | 创建订单应收账单 |
| POST | `/payments` | `createPayment` | 录入收款草稿 |
| POST | `/payments/{id}/confirm` | `confirmPayment` | 财务独立复核收款 |
| POST | `/payments/{id}/allocations` | `allocatePayment` | 确认收款分配至应收 |
| POST | `/attachments/uploads` | `createUpload` | 申请隔离区上传地址 |
| POST | `/integrations/{connection_id}/events` | `receiveIntegrationEvent` | 接收入站集成事件 |

## 尚需扩展

供应商及采购管理、生产节点、检验完整生命周期、收货调拨盘点、报价拒绝撤回、订单补充协议、退货退款、应付付款、报表、权限管理和完整门户接口均不包含在本核心契约中。上传申请也不等于完整附件服务；后续完成上传、扫描和授权下载需要补齐。
