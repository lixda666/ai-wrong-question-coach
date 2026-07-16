# AI 错题教练 (AI Wrong Question Coach)

> 选自「AI 个人系统实践」课程，基于 WorkBuddy Skill 框架构建的 K12 错题分析、复习与可视化系统。

## 项目简介

**AI 错题教练** 是一个面向中小学生的错题智能管理系统。它把"录入错题 → AI 分析错因 → 定位薄弱知识点 → 生成同类变式题 → 自动排复习节奏 → 输出可视化报告"这一传统上需要老师一对一诊断的流程，封装成一个可复用、可扩展的 Skill。

核心价值不在于"套了个 AI 壳"，而在于：
- 错因分析不是给"概念混淆"这种空话，而是定位到具体哪一步哪个公式出了问题
- 复习计划用 **艾宾浩斯 + SM-2 混合模型**，比死记硬背更高效
- 变式题能保留同一知识点的核心、变换表面数字与情境，避免重复做同题
- 报告兼顾 HTML（图表交互）与 Markdown（纯文本可打印）双格式

## 仓库结构

```
.
├── README.md
├── skill/                    # Skill 文件
│   ├── SKILL.md              # 技能定义（含 yaml frontmatter）
│   ├── scripts/              # 5 个 Python 脚本
│   │   ├── mistake_manager.py     # 错题集 CRUD（增删改查）
│   │   ├── mistake_webui.py       # 错题集浏览器界面（基于 Flask）
│   │   ├── progress_tracker.py    # 学习进度追踪
│   │   ├── report_generator.py    # HTML + Markdown 报告生成器
│   │   └── spaced_repetition.py   # 艾宾浩斯 + SM-2 复习排程算法
│   ├── references/           # 参考资料
│   │   ├── config_examples.md     # 配置示例
│   │   ├── error_patterns.md      # 7 类错因模式
│   │   ├── knowledge_points.md    # K12 通用考纲框架
│   │   └── usage_guide.md         # 使用指南
│   └── assets/               # 模板与默认资源
│       └── analysis_template.json
├── data/                     # 测试数据
│   └── 高等数学错题集.md
├── tests/                    # 测试记录
│   ├── test_record.md        # 完整测试记录
│   ├── before_iteration/     # 迭代前产物（v1）
│   ├── after_iteration/      # 迭代后产物（v2）
│   ├── mistake_collection.json
│   └── Clipboard_Screenshot*.png
└── iteration/                # 迭代升级说明
    └── iteration_log.md      # 迭代记录与未来方向
```

## 核心功能

| 功能 | 描述 |
| --- | --- |
| 错题录入 | 支持文字描述、CSV、JSON、Markdown 四种格式 |
| 错因分析 | 基于 `references/error_patterns.md` 的 7 大错误类型分类 |
| 知识点诊断 | 基于 `references/knowledge_points.md` 的 K12 通用考纲框架 |
| 变式题生成 | 同知识点同难度的 1-2 道变式练习 |
| 复习计划 | 艾宾浩斯 + SM-2 混合算法，目标保持率 85% |
| 学习报告 | HTML 交互式（Chart.js 图表）+ Markdown 双格式输出 |
| 错题管理 | 增、删、改、查，Web 界面（`mistake_webui.py`） |
| 进度追踪 | 阶段性总结、保持率曲线、风险预警 |

## 快速使用

### 1. 准备错题集
可以是 Markdown 格式、CSV、JSON 或直接在对话中描述。

### 2. 加载 Skill
将 `skill/` 目录下的文件部署到 WorkBuddy 的 skills 目录中。

### 3. 触发 Skill
对话中提及"错题"、"错题分析"、"复习计划"、"变式题"、"知识点诊断"、"学习报告"等关键词即可触发。

### 4. 生成报告
```bash
python scripts/spaced_repetition.py --input mistakes_input.json --output schedule.json
python scripts/report_generator.py  --input analysis.json --output report
```

## 迭代历程

本项目经历了 **v1 → v2** 两轮迭代：

- **v1（迭代前）**：基础流程跑通，但图表右半空白、UI 偏英文
- **v2（迭代后）**：修复 3 处问题，UI 全中文，图表数据回退到必填字段，复习时间轴可点击查看当天内容

详细迭代记录见 [`iteration/iteration_log.md`](./iteration/iteration_log.md)，测试对比见 [`tests/test_record.md`](./tests/test_record.md)。

## 后续迭代方向

至少 3 个，详见迭代日志：
1. **多学科知识图谱** —— 当前 `knowledge_points.md` 偏数学，需补全理化生政史地
2. **自适应错题推荐** —— 根据保持率动态调整下次复习间隔，而非固定算法
3. **家长 / 老师端协作** —— 支持老师布置作业、自动批改、生成班级错因热力图

## 选题来源

- **学科**：全学科通用（默认从输入自动识别）
- **学段**：动态确认，支持 K12 全学段
- **核心痛点**：抄错题本不思考、同类题反复错、老师没时间一对一诊断

## License

仅作课程作业提交使用。
