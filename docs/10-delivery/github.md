# 上传 GitHub 与日常协作

## 上传前

1. 解压交付包，进入包含 `README.md` 的 `foreign-trade-system-docs` 目录。
2. 运行本地文档校验，检查所有拟提交文件。
3. 由所有者选择仓库账号、名称和可见性；涉及内部设计时先用私有仓库。
4. 确认 `.github`、`.gitignore` 等隐藏目录和文件包含在提交范围中。
5. 不加入真实客户、报价、生产备份、账户资料、环境配置和密钥。

## Git 方式

在 GitHub 创建空仓库，不预先勾选生成 README、许可证和 gitignore。随后在**本交付仓库目录内**执行以下示意命令，先把远程地址替换为自己的仓库地址：

```bash
git init -b main
git status --short
git add .
git diff --cached --stat
git commit -m "docs: initialize foreign trade system documentation"
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
```

`YOUR_ACCOUNT` 与 `YOUR_REPOSITORY` 是待替换标识，不是已经创建的仓库。登录使用 GitHub 支持的认证方式，不把访问令牌写进 URL、命令历史或本库文件。若目录已是 Git 仓库，先检查分支与 remote，不重复初始化或覆盖既有远程。

官方操作依据：[将本地项目添加到 GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)。

## 网页方式

也可在仓库使用 Add file 和 Upload files 上传解压后的文件。上传需要保留目录层级；不要只放一个 ZIP 或遗漏隐藏配置。网页上传有文件大小和批次数量限制，大批量目录或持续维护优先用 Git。[GitHub 文件上传说明](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)。

## CI 和审查

本库附有 [工作流参考模板](../../templates/docs-check.github-actions.yml)，但当前发布凭据不具备工作流写入权限，所以没有启用 GitHub Actions。模板放在 `templates`，不会自动执行。获得相应权限且仓库所有者确认启用后，可将它放入 `.github/workflows/docs-check.yml` 再提交。

启用后的设计是在 push 和 pull_request 时运行格式、链接、生成一致性、Schema、OpenAPI及文档单元测试，工作流只有 contents 读取权限，不负责发布网站或业务服务。启用后仍需查看实际 Actions 结果；本地通过不能证明远程 CI 已成功。

开启分支保护和审查规则由仓库管理员执行。提交应先建立分支，再发起 PR，说明涉及需求、业务规则和测试变化。当前文档库已由所有者授权创建公开仓库 [Ar-Tai/foreign-trade-system-docs](https://github.com/Ar-Tai/foreign-trade-system-docs)；本库不包含 GitHub Pages 或业务服务的部署，也没有代替管理员设置分支保护。

## 打包新的文档版本

本地检查通过后运行 `python scripts/package_release.py`。脚本只打包当前文档仓库，排除虚拟环境、缓存、Git历史和检查产物，默认输出到 `dist`，同时生成 ZIP 的 SHA256 校验文件。它不会替你提交、上传或发布。
