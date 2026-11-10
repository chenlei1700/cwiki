# cwiki — LLM 维护的项目知识库 skill

> 中文（默认） | [English](README.en.md) — 双语文档同步维护；表述如有出入，以英文版为准。
> 操作件（`skill.md`、`templates/`、`tools/`）只有英文单一版本——判据只留一份，不设第二份会漂移的拷贝。

一个 [Claude Code skill](https://docs.claude.com/en/docs/claude-code)：给任何项目装上一套整洁的、由 LLM 维护的 `wiki/` 知识库，**外加让它数月不腐的维护机器**（同步脚本、hook 闸门、漂移检测）。

方法论蒸馏自一个多年期量化研究项目的生产实践（40+ skills、夜间流水线、append-only 账本），再泛化为项目无关。代码项目、研究实验室、事故复盘档案、个人笔记库——凡是想让 LLM 替你组织和交叉引用知识的场景都适用。

## 文档索引

| 我想…… | 读 |
|---|---|
| 判断该不该用这套（跟 star 更多的比） | 本页下一节「为什么是 cwiki」 |
| 理解设计与方法论（为什么长这样） | [docs/architecture.zh.md](docs/architecture.zh.md) |
| 安装（装法/验证/升级/排障） | [INSTALL.zh.md](INSTALL.zh.md) |
| 跑起来：新项目 / 既有项目 | 本页「使用——两种起步场景」 |
| **日常怎么查、怎么更**（12 个分场景流程） | [docs/workflows.zh.md](docs/workflows.zh.md) ⭐ |
| 接自动化（同步/闸门/夜检） | [docs/maintenance-mechanisms.zh.md](docs/maintenance-mechanisms.zh.md) + [tools/](tools/README.md) |
| 查规则细节 | [templates/SCHEMA.md](templates/SCHEMA.md)（英文） |
| skill 的具体行为 | [skill.md](skill.md)（英文） |

## 为什么是 cwiki

Star 更多的工具解决的是**别的问题**——先对号入座：

| 你可能在比较 | 它解决什么 | 它不管、而 cwiki 管的 |
|---|---|---|
| mem0 / Letta(MemGPT) / Zep 等 agent-memory 库 | 给**你开发的应用**提供运行时记忆 API（存向量库/DB） | **你和 LLM 结对开发的项目本身**的知识：人要读、要进 git 被 diff 审查、要跨月不腐。它们不落 markdown，也不治理内容真实性 |
| Obsidian / Logseq | 人手维护的个人知识管理 | 维护者是 LLM 时的失控：谁可以改哪个文件、复制漂移、LLM 宣称的核验。cwiki 的 `[[]]` 与 Obsidian 兼容——可以拿 Obsidian 当浏览器，两者共存 |
| MkDocs / Docusaurus / GitHub Wiki | 把文档渲染成好看的站点 | 内容本身**真不真、新不新**：发布层不检查"当前状态文档与现实矛盾"。cwiki 的产出是纯 markdown，可以直接喂给它们渲染 |
| Notion 等 SaaS wiki | 托管协作文档 | 数据在自己手里；LLM 的每次改动可 git diff 审查；能接 pre-commit / 夜检闸门 |
| TencentDB-Agent-Memory / NVIDIA auto-ontology | 对话记忆抽取与本体治理（服务端） | 同为记忆治理，但形态是服务 + DB；cwiki v3 已把两者值得吸收的点（容量倒逼合并、变更闸门、墓碑、写后回读）消化成 markdown + git 形态 |

cwiki 独有的七个能力（⭐，各自指向出处；[workflows](docs/workflows.zh.md) 里逐场景标注它们在哪一步起作用）：

1. **修改权被执法**——L1/L2/L3 "谁可以编辑这个文件"不是口头约定，是同步脚本 + 闸门强制的（SCHEMA §3）；
2. **纪律变闸门 + 守门员被守**——每条规则是会变红的检查，每个检查带故障注入 `--selftest` 并跑进回归（Mechanism 6、`wiki_lint_skeleton.py`）；
3. **蒸馏回路**——专治 LLM 结对特有的"常驻上下文膨胀"（CLAUDE.md 预算线 + 单条形态闸 + 蒸馏 SOP + 抽查比读）。上面任何竞品都没有这个问题意识（SCHEMA §13）；
4. **新旧仲裁**——多会话并发下"哪份是最新"有固定裁决顺序 + sources 指纹三态 + 墓碑与复活检测（SCHEMA §15）；
5. **探索前查账**——append-only 假设账本让"这个试过没有"有可证明的答案，失败原因与失败本身分开记（SCHEMA §10）；
6. **话题层**——"关于 X 的一切"一个键拉出 内容/进度/历史/会话/代码 五栏（SCHEMA §16）;
7. **零依赖零服务**——纯 markdown + git + 标准库 Python。没有向量库、没有 SaaS、没有锁定：删掉 skill，你的 wiki 照常活着。

**什么时候别用 cwiki**（诚实分流）：要给应用接运行时记忆 API → mem0/Letta/Zep；只要漂亮文档站 → Docusaurus；纯个人手写笔记 → Obsidian 就够。cwiki 的目标用户是**长期用 Claude Code 这类 LLM 结对开发、知识主要由 LLM 产出与维护的项目**——在这个场景里，上面七条每一条都对应一种已经付过学费的腐烂方式（见 [architecture §1](docs/architecture.zh.md)）。

## 你会得到什么

**方法论**（skill.md + templates/）：

- **三层数据模型** —— SSOT（机器真相）/ Derived（自动视图）/ Narrative（手写叙事）。根治"同一事实改三处、互相矛盾"的失败模式。
- **5 个通用页面类别** —— `concepts/`、`experiments/`、`sources/`、`architecture/`，外加你自己的领域目录，各配模板。
- **`[[name]]` 交叉引用** —— Obsidian 兼容，双向回链由 Ingest 流程强制执行。
- **事件路由表** —— `MAINTENANCE_ROUTING.md` 把"这类变更"映射到"必须更新的文件清单"，并带**漏做症状**与**兜底闸**两列，使它同时成为反向诊断索引。
- **Ingest / Query / Lint** 三个具名操作，skill 端到端驱动。
- **规模件（按需启用，每项带明确的采纳触发条件）** —— 依赖 frontmatter + 四层执法、append-only 账本 + 探索前先查账、自动生成页（不覆盖人写段 + 自述空态）、导航层（`ONBOARDING.md` 等）、常驻文档的上下文预算 + 蒸馏 SOP、矛盾结构化（演变轨迹 / 待确认矛盾）、新旧仲裁（sources 指纹、supersedes + 墓碑、固定的"判最新"排序）、把页面/账本/日志/代码缝合在一个查询键后面的话题层。

**机器**（docs/ + tools/）：

- [`docs/workflows.zh.md`](docs/workflows.zh.md) —— **实战流程**：查找 4 场景（历史结论 / 当前状态 / 话题全貌 / 探索查重）+ 更新 8 场景（ingest / 实验落档 / 矛盾 / 订正 / 发布 / 记教训 / 取代删除 / 红灯处置），每场景标注独有能力在哪一步起作用。
- [`docs/architecture.zh.md`](docs/architecture.zh.md) —— 读者总览：问题定义、两根正交轴（修改权 × 注入档位）、方法论七条承诺、组件地图、项目生命周期、明示的局限。**想理解这套系统，从这份读起**；下面几份是拿来操作它的。
- [`docs/maintenance-mechanisms.zh.md`](docs/maintenance-mechanisms.zh.md) —— 完整运转图景：L1→L2 同步契约、append-only 账本、hook 执法（PostToolUse / Stop / pre-commit / 夜检）、新鲜度分级、生成页规则、"纪律变闸门"、运维日历、症状→根因故障索引。
- [`tools/`](tools/README.md)（英文） —— 通用参考实现：`sync_views_example.py`（L1→L2 同步，`--check` 接 pre-commit）、`scan_skill_dependencies.py`（frontmatter 草稿生成）、`check_new_skills_registered.py`（Stop-hook 闸）、`check_dependency_drift.py`（夜间漂移检测）、`wiki_lint_skeleton.py`（机械化 lint 骨架，5 检 + 18 例注入自检）。

## 安装

下面是速览——**[INSTALL.zh.md](INSTALL.zh.md) 是详细指南**：三种模式取舍（全局 / 项目内 / 无 git 拷贝，遮蔽规则）、装后验证、团队仓库的 vendor vs submodule、哪些东西装完并不自动生效（tools 要接线）、各模式的升级方法、故障排查表、卸载。

### 模式 A —— 用户全局（所有项目可用）

```bash
# Windows:
git clone https://github.com/chenlei1700/cwiki "$env:USERPROFILE\.claude\skills\wiki-management"

# macOS / Linux:
git clone https://github.com/chenlei1700/cwiki ~/.claude/skills/wiki-management
```

文件夹名（`wiki-management`）就是 skill 名，想换调用名就改文件夹名。

### 模式 B —— 项目内

```bash
git clone https://github.com/chenlei1700/cwiki .claude/skills/wiki-management
```

然后把它 vendor 进项目（删掉其 `.git`、提交文件），让所有 clone 你项目的人都自动获得 skill——细节与 submodule 替代方案见 [INSTALL.zh.md §1](INSTALL.zh.md)。

装完后**开一个新会话**（skill 在会话启动时加载），按 [INSTALL.zh.md §2](INSTALL.zh.md) 验证。

## 使用 —— 两种起步场景

两种场景装法完全相同，差别只在第一句话。

### 场景 1 —— 全新项目（greenfield）

说 `bootstrap wiki` / `建立 wiki`。skill 约 5 分钟立起 `wiki/SCHEMA.md`、`index.md`、`log.md`、`MAINTENANCE_ROUTING.md`、`ONBOARDING.md` 和起步类别目录（skill.md §2），问一个领域目录问题，当天就能开始 ingest。骨架之外不装任何机器——规模件各等各的触发条件。

### 场景 2 —— 既有项目（brownfield）

说 `adopt wiki` / `把 wiki 方法论用到现有项目`。skill 走 **Adoption 流程**（skill.md §2B）而不是裸 Bootstrap：

1. **只读盘点**既有知识载体——长大的 README/docs、积满教训的 `CLAUDE.md`、机器产物/账本——逐个分层归类，产出一页 adoption map 由你确认。
2. **骨架并行立起**——既有内容一个不动；机器产物**原地**宣告为 L1（搬动会弄断生产者）；采纳日成为所有不回溯闸门的 cutoff。
3. **双车道渐进迁移**——migrate-on-touch（真实工作下次碰到某篇旧文档时顺手迁）+ 积压队列小批量（小文件可走 Mechanism 8 无头驱动：机械验收 + 回滚）。
4. **闸门只按触发条件上**——首日通常只上常驻文档的预算 + 单条形态闸；lint 第一周先 report-only。历史内容永不被回溯执法。

Adoption 存在就是为了拦住那个反模式：把全部旧文档 big-bang 改写成 wiki 格式——丢保真、半途而废，留下两份半真相比一份乱真相更糟。

### 日常操作（两种场景通用，wiki 立起之后）

| 你说 | 发生什么 |
|---|---|
| `ingest this: <材料>` / `把这个加进 wiki` | §3 Ingest —— 分类、建/更宿主页、加 `[[]]` 交叉引用、更新 `index.md` + `log.md` |
| `wiki 里有没有 X` / `query wiki` / `之前对 X 的结论是?` | §4 Query —— 先读 `index.md`，走到候选页，带引用作答 |
| `lint wiki` / `wiki 体检` | §5 Lint —— 孤儿页 / 死链 / 过期 tentative / 三层违规检查 |

skill 是**按需触发**的——只在上述触发语上激活，日常工作不碰你的仓库。

## 仓库结构

```
.
├── skill.md                       # 主指令 (§0–§9)（英文，操作件单一版本）
├── README.md / README.en.md       # 本文件（中文默认）/ 英文版
├── INSTALL.zh.md / INSTALL.md     # 详细安装：中文 / 英文
├── templates/
│   ├── SCHEMA.md                  # 规则书 — 核心 §1–§8 + 规模件 §9–§16（英文）
│   ├── index.md / log.md / MAINTENANCE_ROUTING.md / ONBOARDING.md
│   └── page_types/                # concept / experiment / source / architecture / domain_entity
├── docs/
│   ├── architecture.zh.md / .md   # 读者总览：中文 / 英文 — 先读这份
│   ├── workflows.zh.md / .md      # 实战流程：12 个分场景（查 4 + 更 8），独有能力逐步标注
│   └── maintenance-mechanisms.zh.md / .md   # 维护机器：中文 / 英文
├── tools/                         # 参考实现（拷走 + 改 CONFIG 块；英文）
│   ├── README.md
│   ├── sync_views_example.py
│   ├── scan_skill_dependencies.py
│   ├── check_new_skills_registered.py
│   ├── check_dependency_drift.py
│   └── wiki_lint_skeleton.py      # 机械化夜检骨架（5 检 + selftest）
└── .gitattributes
```

## 设计要点

几个不显然的决策：

- **模板刻意写短** —— 长模板会被当成必填表格；短模板给真实内容留位置。
- **每个规模件都写明采纳触发条件。** 重机器（frontmatter 执法、账本、生成页）过了某个项目规模才回本；提前上只是加仪式。SCHEMA §9–§16 每节开头都是 "Adopt when: ..."。
- **`[[]]` 交叉引用是双向的**：A 页里每加一个 `[[X]]`，X 页里必须出现回链。Ingest 流程强制执行——这是孤儿页不积累的最大单一原因。
- **L1（机器真相）与 L3（叙事）永不共持同一事实。** 数字住在 JSON 账本里，叙事页就链接账本而不是抄数字。这条规则防住最恶性的漂移——对 `CLAUDE.md`/`README.md` 同样适用。
- **写成散文的规则会衰减；接成红色检查的同一条规则不会。** 这个观察（在源项目里反复付过学费）是依赖约定配四层执法、`docs/maintenance-mechanisms.*` 每个机制都以闸门收尾的原因。推论：每个闸门都要故障注入验一次——从没红过的闸门与坏了的闸门无法区分。
- **状态住在结构化字段里，不住散文里。** 一段"这个方向废弃了"的文字对工具不可见；它关掉的方向几个月后会被重新昂贵地探索。关闭/废弃一律打机器可读标记。

## 更新日志

- **v3.3 (2026-11)** —— 定位与可用性：README 加「为什么是 cwiki」（与 mem0/Letta/Zep、Obsidian、Docusaurus、SaaS wiki、腾讯/NVIDIA 记忆系统的诚实对比 + 七条独有能力 + 什么时候别用它）与「文档索引」；新增 docs/workflows（双语）——12 个分场景实战流程（查找 4 + 更新 8），独有能力逐步 ⭐ 标注。
- **v3.2 (2026-11)** —— 双语化：中文成为默认展示（README.md、INSTALL.zh.md、docs/*.zh.md），英文版保留为 README.en.md 及原路径；操作件保持英文单一版本（判据只留一份）。
- **v3.1 (2026-11)** —— 双场景使用路径（§2B Adoption：盘点→共存→双车道渐进迁移→闸门按触发上）；INSTALL.md 详细安装指南；docs/architecture.md 读者总览。
- **v3 (2026-11)** —— 记忆治理回流（调研 TencentDB-Agent-Memory 与 NVIDIA auto-ontology 后在生产中实测）：SCHEMA §13 上下文预算 + 蒸馏 SOP（注入档位、两档退役、蒸馏账本、抽查比读、单条形态闸）；§14 矛盾结构化；§15 新旧仲裁（sources 指纹三态、supersedes + 墓碑与复活检测、固定"判最新"排序）；§16 话题层；Mechanism 7（蒸馏回路）与 8（外部 assistant-memory 主权 + 无头迁移驱动的机械验收模式）；`tools/wiki_lint_skeleton.py`；"守门员也要被守"接线说明。
- **v2 (2026-10)** —— 从源项目同步演进设计：SCHEMA 规模件 §9–§12、路由表 v2 模式、`ONBOARDING.md` 模板、`docs/maintenance-mechanisms.md`、`tools/` 参考实现、`.gitattributes`（LF 归一）。
- **v1 (2026-05)** —— 首版：三层模型、5 类别、路由表、Ingest/Query/Lint。

## 许可

MIT —— 随意使用。若你以有趣的方式扩展了这套方法论，欢迎 PR。
