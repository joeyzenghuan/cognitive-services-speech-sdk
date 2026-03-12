# Copilot Instructions

## Git 工作流

这个项目是从 Azure-Samples 官方仓库 fork 来的，有两个 remote：

- `origin`：Azure 官方仓库
- `myfork`：我的 fork（joeyzenghuan）

当需要同步官方更新或推送修改时，使用以下流程：

```bash
git add . && git commit -m "修改说明"
git fetch origin
git rebase origin/master
git push --force myfork my-customizations
```

注意：rebase 后必须用 `--force` 推送。如果 rebase 遇到冲突，解决后用 `git add . && git rebase --continue`。
