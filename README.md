# matt

这个仓库用来跑 Matt Pocock 的 engineering skills 工作流：想法先被追问打磨，再落成 spec 和 tickets，最后按 ticket 实现。issue 存在 GitHub，配置和术语都放在仓库里，换机器时克隆即可。

## 最短路径

1. 有想法时用 `$grill-with-docs` 追问，顺带产出术语和决策记录。
2. 用 `$to-spec` 把讨论整理成 spec，发布为 issue 并打 `ready-for-agent`。
3. 用 `$to-tickets` 拆成 tracer-bullet tickets，用 native blocking 声明依赖。
4. 用 `$triage` 把新 issue 在五个状态之间推进。
5. 用 `$implement` 领 ticket 实现：先测试后实现，跑完整测试，最后 code review。

## 文件在哪

| 想找什么 | 看哪里 |
| --- | --- |
| 术语的唯一定义 | `GLOSSARY.md` |
| issue 怎么建、怎么读、怎么关闭 | `docs/agents/issue-tracker.md` |
| triage 标签映射 | `docs/agents/triage-labels.md` |
| 术语表和 ADR 的消费规则 | `docs/agents/domain.md` |
| 架构决策记录 | `docs/adr/` |
| 给 agent 的仓库约定 | `AGENTS.md` |

## 前置条件

需要 `gh` CLI 并已登录：

```powershell
gh auth status
gh repo view --json nameWithOwner
```

第二条应输出 `yunzhan03/matt`。不在仓库目录里运行 skills 时，配置不会生效。

## 现状

仓库目前只有工作流配置与文档，还没有业务代码。
