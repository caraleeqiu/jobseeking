# 求职 Copilot

针对 **创业公司 Founding / Growth Marketing** 岗位的半自动求职助手。
不海投，专注两件高转化的事，全部中英双语输出：

- **腿 A · 岗位定制**：粘一段 JD → 匹配度打分 + 针对性简历要点 + 求职信
- **腿 B · 创始人触达**：公司+创始人信息 → 个性化 cold outreach（邮件 + LinkedIn DM）

底层用 Google Gemini（默认 gemini-2.5-flash）。你**基本不用碰代码**：改一个画像文件、把 JD/公司信息粘进文本文件、跑一行命令即可。

---

## 一次性准备（约 5 分钟）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
#    然后编辑 .env，填入你的 Google (Gemini) API Key
#    Key 获取地址：https://aistudio.google.com/apikey

# 3. 配置你的画像
cp config/profile.example.yaml config/profile.yaml
#    然后编辑 config/profile.yaml，填入你的简历 + 求职范围偏好
```

> `config/profile.yaml`、`.env`、你自己的 `jobs/*.md` 和 `companies/*.md`
> 都已被 `.gitignore`，**不会被提交或上传**，可以放心填真实信息。

---

## 日常使用

### 腿 A：定制一个岗位

1. 把 JD 整段粘到一个文件，比如 `jobs/acme.md`
2. 运行：

```bash
python main.py tailor jobs/acme.md
```

3. 结果写到 `output/acme-tailored.md`，包含：匹配度、范围契合判断、优势、差距+补法、定制简历要点（中英）、求职信（中英）。

### 腿 B：给某个创始人写触达

1. 把你研究到的公司 + 创始人信息粘到一个文件，比如 `companies/acme.md`（越具体越好；缺的部分模型不会编）
2. 运行：

```bash
python main.py outreach companies/acme.md
```

3. 结果写到 `output/acme-outreach.md`，包含：切入点、痛点假设、为什么是你、邮件（含 3 个标题，中英）、LinkedIn DM（中英）。

> 默认会**联网检索**公司近期动态（融资/发布/创始人动态）并自动引用，让触达更有杀伤力。
> 不想联网就加 `--no-research`：
> `python main.py outreach companies/acme.md --no-research`

先拿仓库里自带的 `jobs/example-job.md` 和 `companies/example-company.md` 试跑，感受一下输出。

---

## 项目结构

```
main.py                 命令行入口（tailor / outreach）
config/profile.yaml     你的画像（简历 + 求职范围偏好）← 改这里
jobs/*.md               你要投的 JD（一个岗位一个文件）
companies/*.md          你研究的公司/创始人信息
output/*.md             生成的报告
src/                    程序逻辑（一般不用动）
```

---

## 设计原则

- **半自动，不无人值守**：机器负责搜集、打分、起草，**最后由你确认提交**——更安全、更高质量。
- **不编造**：所有简历要点、数字都只来自你的画像；公司信息只用你提供的。
- **打分含范围过滤**：匹配度会同时考虑你的 stage / 职能 / 地区 / remote 偏好，明显不合适的会被点出来并打低分。
- **省钱**：默认用 gemini-2.5-flash；画像作为稳定前缀，Gemini 2.5 会隐式缓存复用。要更高质量可在 `.env` 设 `GEMINI_MODEL=gemini-2.5-pro`。

## 路线图（后续可加）

- 岗位聚合抓取（多渠道）+ 自动打分排序看板
- ~~创始人触达接入 web 检索，自动引用公司最新动态~~ ✅ 已完成（默认开启）
- 投递追踪看板（待投/已投/面试/拒信）
