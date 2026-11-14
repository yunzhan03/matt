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

## 数据契约

`src/alloydata/` 实现了第一条可执行链路：把一条记录（或一份 CSV）交给校验器，得到结构化错误，而不是靠人肉检查。

```python
from alloydata.validate import validate_record

issues = validate_record(record)  # record 是 dict，字段契约见 src/alloydata/record.py
```

运行测试：

```powershell
python -m unittest discover -s tests
```

## Cursor 桥接自检

`tools/cursor-bridge-check.ps1` 按顺序检查五件事：桥接 `status.json`、代理端口、Cursor 的 `http.proxy`、本地根证书、Magpie 网关，一行一个结论，最后给 `VERDICT`。

```powershell
powershell -ExecutionPolicy Bypass -File tools\cursor-bridge-check.ps1
powershell -ExecutionPolicy Bypass -File tools\cursor-bridge-check.ps1 -Fix
```

不加 `-Fix` 只读诊断；加 `-Fix` 会重跑插件 setup、必要时拉起 supervisor，然后复检。退出码 0 表示全绿，1 表示仍有失败项。

已知失效点：`status.json` 停在 `disconnected`、`52407` 无监听、`http.proxy` 被还原——三者通常同时出现，说明后台 supervisor 没在跑，而 Magpie 界面会照旧显示「已接入」。

## 现状

已有工作流配置、文档，以及零依赖的记录校验器（21 个测试）；尚无真实数据与模型代码。
