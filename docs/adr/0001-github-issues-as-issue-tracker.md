# 0001: 用 GitHub Issues 作为 issue tracker

## Status

Accepted

## Context

本仓库的 skills（`$to-spec`、`$to-tickets`、`$triage`、`$wayfinder`）都要读写一个 issue tracker，并且需要 label、sub-issue 和 native blocking 这些能力。仓库是新建的 public 仓库 `yunzhan03/matt`，目前只有文档，没有多包结构。

## Decision

issue 与 spec 一律存在本仓库的 GitHub Issues，统一用 `gh` CLI 操作。仓库根部的 `docs/agents/issue-tracker.md` 是操作手册，`AGENTS.md` 里的 `## Agent skills` 段指向它。

## Consequences

- 需要本机安装 `gh` 并已登录；未登录时所有读写操作都会失败。
- issue 编号在 issue 与 PR 之间共享，解析裸 `#42` 时要先判断类型。
- 仓库是 public，issue 内容对外可见，写之前要按公开信息处理。
- 支持 native sub-issue 与 native blocking，ticket 依赖不必退化成正文里的文字。

## Alternatives considered

- **本地 `.scratch/<feature>/` markdown**：无需网络和账号，但 issue 不能被外部看到，也没有 native blocking，多人协作和移动端都不方便。否决。
- **GitLab Issues**：本仓库没有 GitLab remote，也没有 `glab` 凭据。否决。
- **Jira / Linear 等外部 tracker**：为纯文档仓库额外引入账号和同步成本，收益不足。否决。
