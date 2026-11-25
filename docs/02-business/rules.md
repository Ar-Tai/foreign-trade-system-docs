# 业务不变量与计算规则

## 数量不变量

- 订单净有效数量等于原始订购数量加已批准变更，历史出运不被覆盖。
- 每一订单行的累计有效出运量不得超过净有效数量，允许欠交时另建批准记录。
- 每一库存桶中 `on_hand >= 0`、`reserved >= 0`、`blocked >= 0`，并且 `reserved + blocked <= on_hand`。
- `available = on_hand - reserved - blocked`。三个数量均采用同一基础单位。
- 冻结已有预留时，先撤销或转移该预留对应数量，再转入冻结分区；不得让同一物理单位同时属于两个分区。
- `dispatch` 同时减少在手和预留；取消未发预留只减少预留，不增加在手。
- 调拨出库形成在途，目的仓实际收货后再增加在手；部分丢损通过差异处置处理。

## 金额不变量

以订单约定币种逐行计算商品净额，再汇总费用和经确认的税费项目。订单金额以冻结的明细为准。商品单价、数量、百分比、汇率均不得使用二进制浮点做账务计算。

本示例对 USD 与 CNY 使用两位小数、四舍五入 HALF_UP；生产系统应按配置币种精度执行，不能把两位小数规则套用于所有币种。单位价格可保留更多小数，行金额按明确规则舍入。分摊先计算高精度结果，再把尾差分配至规则指定的最后一项。

```text
line_net = round(quantity × unit_price - line_discount, currency_scale)
order_total = sum(line_net) + sum(charges) + sum(explicit_tax_items)
unallocated_payment = confirmed_gross_amount - active_allocations
invoice_open = invoice_amount - credit_adjustments - active_allocations
contribution = recognized_order_revenue - allocated_order_costs
```

示例不设税费，表示未演示税务情形，不表示该交易依法免税。生产实现需明确销售折让、退款、贷项调整和坏账的不同含义。

## 核销约束

一笔有效分配同时属于同租户、同收款方范围内的款项和应收账单。分配额不能超过两边余额。跨币种支付先通过明确的换汇或结算记录转换，不能在核销接口隐式套用最新汇率。确认与冲销必须锁定涉及余额，以避免并发超分配。

## 汇率约束

`base_currency=USD`、`quote_currency=CNY`、`rate=7.2` 表示 1 USD 对应 7.2 CNY。从 CNY 换至 USD 用除法。每笔成本保留原币金额、报告币金额、汇率来源、日期和舍入差异。缺失汇率时阻断换算，不使用 1 作为兜底。

## 单据与审计

单据号按租户和单据类型唯一，不依赖连续无缺号作为业务正确性依据。已确认业务保留快照，不通过更新产品或客户主数据修改历史。已发生业务效果的记录原则上采用停用、取消、冲销及新版本，不直接物理删除。
