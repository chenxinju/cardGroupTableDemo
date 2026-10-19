# RenameTool — iOS 类名混淆可视化工具

参考 [LSUnusedResources](https://github.com/tinymind/LSUnusedResources) 的操作方式：选择工程目录 → 配置参数 → 一键运行 → 查看日志与 mapping。

## 整合策略

| 来源 | 保留能力 |
|------|----------|
| **Rename_V2.5_input_output_mapping.py** | input/output mapping、发版复用旧映射、多任务、父目录前缀自动继承、`maps_dir` |
| **Rename_V2.3_Viven.py** | Xcode 文件头 `Created by` 批量更新 |

整合入口脚本：`Scripts/Rename_merged.py`（支持 `--config` JSON，供 GUI 调用）。  
原版脚本原样保留在 `Scripts/` 与 `GroupShadowTableView-master/Rename/`。

## 打开可视化工程

1. 用 Xcode 打开：
   ```
   /Volumes/D/githubDemo/cardGroupTableDemo/ObfuscationTool/RenameTool.xcodeproj
   ```
2. 选择 scheme **RenameTool**，⌘R 运行。
3. 本工具是 **并列的 macOS App**，不会改动 `cardGroupTableDemo` / `GroupShadowTableView` demo。

## 界面用法

1. **源码根目录 project_path**：含业务源码的目录（脚本会在此递归改 `.h/.m/.swift`）。
2. **maps_dir**：存放 `*_mapping.json` 的目录（建议单独建 `ReleaseMaps`）。
3. **target_folder**：本次要处理的子目录。
4. **旧/新前缀**：逗号分隔；子模块任务可留空前缀（脚本按 V2.5 规则从父任务继承——多任务请用 JSON 配置）。
5. 勾选：
   - **仅替换前缀** / **完全重命名**
   - **复用旧 mapping**（推荐发版时打开）
   - **回滚模式**（用已有 mapping 还原）
   - **更新文件头 Created by**（V2.3 能力）
6. 点击 **开始混淆**，下方看日志；结束后 **刷新 Mapping** 查看 old→new 表。
7. 运行前请先 **git commit** 备份；出问题优先 `git checkout .`。

> GUI 当前一次提交 **一个任务**。若需要 Global → Home → Mine 多阶段流水线，请编辑 `Scripts/example_config.json` 后用命令行跑 `Rename_merged.py --config ...`。

## 命令行

```bash
cd ObfuscationTool/Scripts
python3 Rename_merged.py --config example_config.json
# 仅打印解析后的任务：
python3 Rename_merged.py --config example_config.json --dry-print-config
```

JSON 字段说明见 `Scripts/example_config.json`。

## 目录结构

```
ObfuscationTool/
├── README.md
├── RenameTool.xcodeproj/     # macOS 可视化工程
├── RenameTool/               # App 源码（Swift + 程序化 UI）
└── Scripts/
    ├── Rename_merged.py      # 整合脚本（推荐）
    ├── Rename_V2.5_input_output_mapping.py
    ├── Rename_V2.3_Viven.py
    └── example_config.json
```

## 注意

- 混淆会改源码与 `project.pbxproj`，务必先备份。
- 不要把运行产生的 `Fascine_*.json` / 业务 mapping 误当成「工具源码」提交（除非刻意当样例）。
