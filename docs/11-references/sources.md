# 原始资料与适用范围

以下官方资料用于核对分类、技术格式及 GitHub 操作边界。业务模块、需求与演示数据为本仓库的设计方案，不代表这些机构认可本系统。核对日期为 2026年11月24日。

| 资料 | 用于支持 | 不能据此推出 |
| --- | --- | --- |
| [WCO HS 分类资料](https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition.aspx) | 国际货物分类与业务类目不同 | 任意商品的最终编码或税率 |
| [联合国 CPC](https://unstats.un.org/unsd/classifications/Econ/CPC) | 产品分类包括货物与服务 | 本书编号等同官方分类 |
| [GS1 GPC](https://www.gs1ie.org/standards/data-exchange/global-product-classification-gpc/) | 商品分类与属性可分层表达 | 品类编号就是商品唯一标识 |
| [ICC Incoterms 2020](https://iccwbo.org/business-solutions/incoterms-rules/incoterms-2020/) | 贸易术语表达交易责任安排 | 自动决定所有权 付款或适用法律 |
| [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html) | 接口契约文件的技术格式 | 接口已经部署或业务正确 |
| [OWASP ASVS](https://asvs.owasp.org/) | Web应用安全验证参考框架 | 系统已获认证或评估通过 |
| [GitHub 本地仓库上传](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github) | 初始化和推送流程 | 本交付已经发布到远程 |
| [GitHub 文件上传](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository) | 网页上传方法与限制 | 上传成功等于应用已运行 |
| [固定的 checkout 动作提交](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683) | 文档CI采用的已核对动作版本 | 此版本永久适用或永无漏洞 |

具体产品、市场和日期的监管要求应再核实。本库不提供实时报价、税率库、制裁名单或全球统一的合规许可结论。
