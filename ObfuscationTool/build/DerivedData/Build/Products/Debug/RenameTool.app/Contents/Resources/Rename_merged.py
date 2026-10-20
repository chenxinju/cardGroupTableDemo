import os
import re
import random
import json
from datetime import datetime




"""
iOS 项目类名混淆工具 整合版（V2.5 mapping + V2.3 文件头）

也可由 GUI / CLI 传入 JSON：python3 Rename_merged.py --config /path/config.json

原 v2.5 使用说明

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【换新项目时，只需修改这三处】

  1. PROJECT_CONFIG — 填项目路径和 mapping 保存目录
       'project_path': '你的 Xcode 源码根目录（含 .xcodeproj 的那一层）'
       'maps_dir':     '存放 mapping 文件的目录，随便一个固定路径即可'

  2. TASK_CONFIGS_RAW — 填前缀和目标目录
     Global 任务（父目录，only_modify_prefix=True）必须填三个字段：
       'old_prefixes':  ['旧前缀1', '旧前缀2']   # 项目原有的类名前缀
       'new_prefixes':  ['新前缀1', '新前缀2']   # 混淆后的类名前缀
       'target_folder': '要处理的文件夹路径'

     子模块任务（Home/Mine 等子目录）只需一个字段：
       'target_folder': '子目录路径'
       # old_prefixes / new_prefixes 不填，脚本自动从父目录任务继承

  3. middle_word_groups（可选）— 替换成你想要的随机词汇
     三组单词，每次从中随机抽取 2~3 个组合成类名中间部分
     建议用 4~8 个字母的英文单词，不要用已有的 iOS 类名关键词

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【使用步骤】

  Step 1  git commit 备份当前代码（出问题用 git checkout . 一键还原）
  Step 2  按上方说明修改配置
  Step 3  终端运行：python3 Rename_V2.5_input_output_mapping.py
  Step 4  Xcode Build（Cmd+B）验证编译通过
  Step 5  以后每次发版直接运行脚本，旧类名自动复用，新增类自动生成新名字

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【多任务关键规则】

  本项目使用两阶段混淆：
    Global 任务（only_modify_prefix=True）先跑，只替换前缀
      QGHomeView → FZHomeView

    Home / Mine 任务（only_modify_prefix=False）后跑，做完全重命名
      FZHomeView → FZBridgeRelayView（前缀 + 随机中间词 + 后缀）

  ⚠️  规则一：任务顺序不能改，Global 必须排在 Home / Mine 之前
  ✅  规则二（已自动处理）：脚本启动时会自动检测目录包含关系，
              把父目录任务的 new_prefixes 补入子目录任务的 old_prefixes，
              运行时会打印「🔗 自动继承前缀」日志，无需手动配置

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【回滚】

  推荐：git checkout .
  备用：把对应任务设置 'rollback_mode': True，注释掉其他任务，运行脚本

"""

# ==================== 任务配置区域 ====================
# 每次换项目只需修改这里

# 1. 项目公共配置
PROJECT_CONFIG = {
    'project_path': '',  # 请用 GUI 或 --config 传入
    'maps_dir':     '',
}


# 🆕 文件头版权信息配置（来自 V2.3）
# 也可在 JSON config 的 copyright_header / 任务级 copyright_header_config 覆盖
COPYRIGHT_HEADER_CONFIG = {
    'enabled': False,                 # True: 开启文件头版权信息更新 / False: 关闭
    'author_name': '',                # Created by 后面的名称
    'scope': 'target_folder',         # target_folder / project
    'scan_header_lines': 30,
}


# 2. 全局默认值（各任务可单独覆盖）
TASK_DEFAULTS = {
    'only_modify_prefix': False,   # True: 只替换前缀 / False: 完全重命名
    'rollback_mode':      False,   # True: 回滚模式（用已有 mapping 还原）
    'use_mapping_reuse':  True,    # 复用旧 mapping，新增类才重新生成
    'only_current_level': False,   # False: 递归处理子目录
}

_P = PROJECT_CONFIG['project_path']

# 3. 任务列表 —— 每个任务只填写名称、前缀、目标目录（不同的才写）
#    output_mapping_file / rollback_mapping_file / pbxproj_path 会自动推导
#    如需回滚，把对应任务的 rollback_mode 改为 True 即可
TASK_CONFIGS_RAW = [
    # 默认留空：请通过可视化工具或 --config JSON 传入任务。
    # 原 V2.5 示例任务见同目录 Rename_V2.5_input_output_mapping.py

]

def guess_pbxproj_path(project_path):
    """从 project_path 推导 project.pbxproj。

    project_path 常见为:
      .../AppName/Sources  →  .../AppName.xcodeproj/project.pbxproj
      .../AppName          →  .../AppName/AppName.xcodeproj/... 或旁侧 AppName.xcodeproj
    切勿用 basename(project_path) 直接拼 Sources.xcodeproj（会指向不存在的路径）。
    """
    if not project_path:
        return ''
    root = os.path.abspath(project_path.rstrip('/'))
    parent = os.path.dirname(root)
    grand = os.path.dirname(parent)
    base = os.path.basename(root)
    parent_name = os.path.basename(parent)
    candidates = []
    # .../VivenHealth/Sources → sibling .../VivenHealth.xcodeproj (parent's parent / parent_name)
    if base.lower() in ('sources', 'source', 'classes', 'code'):
        candidates.append(os.path.join(grand, parent_name + '.xcodeproj', 'project.pbxproj'))
        candidates.append(os.path.join(parent, parent_name + '.xcodeproj', 'project.pbxproj'))
    candidates.extend([
        os.path.join(root, base + '.xcodeproj', 'project.pbxproj'),
        os.path.join(parent, parent_name + '.xcodeproj', 'project.pbxproj'),
        os.path.join(parent, base + '.xcodeproj', 'project.pbxproj'),
        os.path.join(grand, parent_name + '.xcodeproj', 'project.pbxproj'),
    ])
    # de-dupe preserve order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    for c in uniq:
        if os.path.exists(c):
            return c
    return uniq[0] if uniq else ''


def _build_task_configs():
    """将简化配置展开为完整任务配置，自动推导重复字段"""
    project_path = PROJECT_CONFIG['project_path']
    maps_dir     = PROJECT_CONFIG['maps_dir']
    pbxproj_path = guess_pbxproj_path(project_path)
    configs = []
    for raw in TASK_CONFIGS_RAW:
        task = {**TASK_DEFAULTS, **raw}
        task.setdefault('project_path', project_path)
        # 空字符串也算「未指定」，避免 GUI 漏填时 setdefault 写死错误路径
        if not (task.get('pbxproj_path') or '').strip():
            task['pbxproj_path'] = pbxproj_path
        else:
            task.setdefault('pbxproj_path', pbxproj_path)
        if not task.get('output_mapping_file'):
            name_slug = re.sub(r'[^a-zA-Z0-9]+', '_', task['name']).lower()
            task['output_mapping_file'] = os.path.join(maps_dir, f'{name_slug}_mapping.json')
        # input 默认与 output 指向同一文件：首次运行文件不存在自动跳过，后续运行自动读取并合并
        task.setdefault('input_mapping_file', task['output_mapping_file'])
        task.setdefault('rollback_mapping_file', task['output_mapping_file'])
        configs.append(task)

    # 自动前缀继承：
    # 完全重命名任务（only_modify_prefix=False）若目标目录是某个仅前缀任务的子目录，
    # 则自动从该父任务继承 old_prefixes / new_prefixes，子任务可完全不填这两个字段。
    for i, task in enumerate(configs):
        if task.get('only_modify_prefix'):
            continue

        task_target = os.path.abspath(task['target_folder'])
        parent = None
        for predecessor in configs[:i]:
            if not predecessor.get('only_modify_prefix'):
                continue
            pred_target = os.path.abspath(predecessor['target_folder'])
            try:
                if os.path.commonpath([pred_target, task_target]) == pred_target:
                    parent = predecessor
                    break
            except ValueError:
                pass

        if parent is None:
            continue

        # old_prefixes 未填：直接用父任务的 new_prefixes
        if not task.get('old_prefixes'):
            task['old_prefixes'] = list(parent['new_prefixes'])
            print(f"🔗 [{task['name']}] old_prefixes 自动继承自 [{parent['name']}]: {task['old_prefixes']}")
        else:
            # 已填了部分前缀：把父任务 new_prefixes 中缺失的追加进去
            existing = set(task['old_prefixes'])
            extra = [p for p in parent['new_prefixes'] if p not in existing]
            if extra:
                task['old_prefixes'] = task['old_prefixes'] + extra
                print(f"🔗 [{task['name']}] old_prefixes 自动补充 {extra}（来自 [{parent['name']}]）")

        # new_prefixes 未填：继承父任务的 new_prefixes
        if not task.get('new_prefixes'):
            task['new_prefixes'] = list(parent['new_prefixes'])
            print(f"🔗 [{task['name']}] new_prefixes 自动继承自 [{parent['name']}]: {task['new_prefixes']}")

    return configs

TASK_CONFIGS = _build_task_configs()

# 🆕 多组后缀配置 - 支持一次运行处理多种后缀类型
suffix_groups = [
                 {
                 'name': 'Controller',
                 'old_suffixes': ['Controller', 'ViewController', 'Ctrl', 'VC'],
                 'new_suffixes': ['VC', 'ViewController', 'ViewCtrl']
                 },
                 {
                 'name': 'ViewModel',
                 'old_suffixes': ['ViewModel', 'Info', 'VM'],
                 'new_suffixes': ['VM', 'ViewModel']
                 },
                 {
                 'name': 'View',
                 'old_suffixes': ['View', 'CellItem', 'Header', 'ViewItem'],
                 'new_suffixes': ['View', 'InfoView']
                 },
                 {
                 'name': 'Cell',
                 'old_suffixes': ['Cell'],
                 'new_suffixes': ['Cell']
                 },
                 {
                 'name': 'Service',
                 'old_suffixes': ['Manager', 'Service', 'Helper', 'Handler', 'Worker'],
                 'new_suffixes': ['Service', 'Agent', 'Provider']
                 },
                 {
                 'name': 'Utility',
                 'old_suffixes': ['Utils', 'Util', 'Tool', 'Config', 'Utilities'],
                 'new_suffixes': ['Kit', 'Suite', 'Tool']
                 },
                 {
                 'name': 'Network',
                 'old_suffixes': ['Api', 'Request', 'Response', 'Client', 'Session'],
                 'new_suffixes': ['Fetch', 'Query', 'Reply']
                 },
                 ]


# 中间词库（三组单词）frezz
# middle_word_groups = [
#     # Group 1 - 实体词：像功能模块或产品组件名，自然不造作
#     [
#         "Bridge", "Stone",  "Pulse",  "Forge",  "Vault",  "Crest",  "Arrow",  "Ember",  "Prism",  "Bloom",
#         "Drift",  "Shard",  "Comet",  "Flare",  "Haven",  "Nexus",  "Quartz", "Ridge",  "Spire",  "Thorn",
#         "Vortex", "Amber",  "Coral",  "Epoch",  "Fable",  "Glyph",  "Harbor", "Ivory",  "Jasper", "Lancer"
#     ],

#     # Group 2 - 架构词：系统/技术概念，iOS 项目中天然存在
#     [
#         "Chain",  "Frame",  "Layer",  "Mesh",   "Queue",  "Stack",  "Token",  "Block",  "Cache",  "Guard",
#         "Hook",   "Scope",  "Stage",  "Track",  "Batch",  "Depot",  "Kernel", "Matrix", "Module", "Packet",
#         "Portal", "Relay",  "Router", "Schema", "Signal", "Stream", "Thread", "Tunnel", "Vector", "Cipher"
#     ],

#     # Group 3 - 修饰词：形容词转名词风格，增加组合多样性
#     [
#         "Nimble", "Solid",  "Sharp",  "Bright", "Vivid",  "Static", "Fluid",  "Crisp",  "Dense",  "Clean",
#         "Smart",  "Rapid",  "Prime",  "Elite",  "Ultra",  "Turbo",  "Micro",  "Macro",  "Hyper",  "Fiber",
#         "Pixel",  "Cubic",  "Polar",  "Sonic",  "Lunar",  "Solar",  "Terra",  "Cyber",  "Neon",   "Atlas"
#     ]
# ]

# 中间词库（三组单词）PebbleSeeQ
# middle_word_groups = [
#     # Group 1 - 实体词：自然意象与物理组件，适合做模块或工具类名
#     [
#         "Orbit",  "Tide",   "Spark",  "Anvil",  "Beacon", "Chisel", "Dusk",   "Flint",  "Gale",   "Hearth",
#         "Knot",   "Loom",   "Mist",   "Onyx",   "Pine",   "Quill",  "Rune",   "Silk",   "Torch",  "Umbra",
#         "Veil",   "Wren",   "Zephyr", "Aspen",  "Bolt",   "Clay",   "Dawn",   "Fern",   "Grit",   "Halo"
#     ],

#     # Group 2 - 架构词：底层机制与数据流转，伪装成系统基础组件
#     [
#         "Agent",  "Buffer", "Cell",   "Codec",  "Core",   "Daemon", "Engine", "Filter", "Gate",   "Hub",
#         "Index",  "Joint",  "Link",   "Map",    "Node",   "Op",     "Pipe",   "Proxy",  "Ring",   "Slot",
#         "Span",   "Store",  "Sync",   "Tab",    "Unit",   "Valve",  "View",   "Wire",   "Zone",   "Dock"
#     ],

#     # Group 3 - 修饰词：状态、质感与维度，组合后极具技术感
#     [
#         "Agile",  "Bold",   "Clear",  "Deep",   "Fast",   "Grand",  "Hard",   "Iron",   "Keen",   "Lean",
#         "Main",   "New",    "Open",   "Pure",   "Raw",    "Safe",   "True",   "Vast",   "Wide",   "Zero",
#         "Base",   "Dual",   "Flex",   "Gold",   "High",   "Lite",   "Mono",   "Next",   "Pro",    "Swift"
#     ]
# ]

# 中间词库（三组单词）HeyLens
middle_word_groups = [
    # Group 1 - 实体词：自然意象与物理组件（替换为更具质感与微观/宏观意象的词）
    [
        "Prism",  "Forge",  "Nexus",  "Pulse",  "Relay",  "Shard",  "Spire",  "Tether", "Vortex", "Warp",
        "Aegis",  "Braid",  "Crest",  "Drift",  "Ember",  "Flux",   "Glyph",  "Hinge",  "Iris",   "Jolt",
        "Lance",  "Mosaic", "Nebula", "Omen",   "Pivot",  "Quartz", "Ridge",  "Surge",  "Thorn",  "Umbra"
    ],

    # Group 2 - 架构词：底层机制与数据流转（替换为更偏向计算抽象与系统拓扑的词）
    [
        "Bus",    "Cache",  "Chunk",  "Datum",  "Edge",   "Frame",  "Graph",  "Heap",   "Latch",  "Mesh",
        "Queue",  "Realm",  "Scope",  "Trace",  "Union",  "Vault",  "Wave",   "Yield",  "Batch",  "Chain",
        "Delta",  "Event",  "Field",  "Guard",  "Hash",   "Layer",  "Macro",  "Patch",  "Route",  "Stack"
    ],

    # Group 3 - 修饰词：状态、质感与维度（替换为更具工程感与性能暗示的词）
    [
        "Async",  "Bound",  "Cached", "Dense",  "Eager",  "Fixed",  "Global", "Hybrid", "Inline", "Just",
        "Lazy",   "Local",  "Mutable","Nested", "Opaque", "Prime",  "Quiet",  "Static", "Typed",  "Ultra",
        "Volatile","Weak",  "Xeno",   "Yielded","Zoned",  "Atomic", "Binary", "Coarse", "Direct", "Exact"
    ]
]

# 支持的文件类型
suf_set = ('.h', '.m','.mm', '.swift','.pch')


# ==================== 文件头版权信息处理（来自 V2.3） ====================

def get_current_xcode_header_date():
    """生成 Xcode 文件头日期，格式：yyyy/M/d，不补 0"""
    now = datetime.now()
    return f"{now.year}/{now.month}/{now.day}"

def get_copyright_header_config(task_config):
    """读取文件头版权信息配置，支持任务级覆盖全局配置"""
    config = dict(COPYRIGHT_HEADER_CONFIG)
    task_header_config = task_config.get('copyright_header_config')

    if task_header_config is False:
        config['enabled'] = False
    elif isinstance(task_header_config, dict):
        config.update(task_header_config)

    return config

def update_xcode_created_by_header(file_content, author_name, current_date, scan_header_lines=30):
    """
    更新 Xcode 文件头中的 Created by 行：
    //  Created by xxx on 2025/3/6.
    ->
    //  Created by 指定名称 on 当前日期.
    """
    lines = file_content.splitlines(keepends=True)
    if not lines:
        return file_content, False

    created_by_pattern = re.compile(
        r'^(\s*//\s*Created by\s+)(.*?)(\s+on\s+)'
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})(\.?)(\r?\n?)$'
    )

    limit = min(max(int(scan_header_lines or 30), 1), len(lines))
    for index in range(limit):
        line = lines[index]
        match = created_by_pattern.match(line)
        if not match:
            continue

        newline = match.group(6)
        new_line = f"{match.group(1)}{author_name}{match.group(3)}{current_date}.{newline}"
        if line == new_line:
            return file_content, False

        lines[index] = new_line
        return ''.join(lines), True

    return file_content, False

def should_update_copyright_header_file(file_path, task_config, header_config):
    """判断某个文件是否需要参与文件头版权信息更新"""
    if not file_path.endswith(suf_set):
        return False

    scope = header_config.get('scope', 'target_folder')
    if scope == 'project':
        return True

    return is_in_target_folder(file_path, task_config)

def update_task_file_headers(task_config):
    """按任务配置批量更新 Xcode 文件头 Created by 信息"""
    header_config = get_copyright_header_config(task_config)
    if not header_config.get('enabled', False):
        print("ℹ️ 文件头版权信息更新已关闭")
        return 0

    author_name = str(header_config.get('author_name', '')).strip()
    if not author_name:
        print("⚠️ 文件头版权信息更新跳过：author_name 为空")
        return 0

    current_date = get_current_xcode_header_date()
    scan_header_lines = header_config.get('scan_header_lines', 30)
    project_path = task_config['project_path']

    print(f"\n🧾 更新文件头版权信息...")
    print(f"  - Created by: {author_name}")
    print(f"  - 日期: {current_date}")
    print(f"  - 范围: {header_config.get('scope', 'target_folder')}")

    updated_count = 0
    scanned_count = 0
    no_header_count = 0

    for (root, dirs, files) in os.walk(project_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if not should_update_copyright_header_file(file_path, task_config, header_config):
                continue

            scanned_count += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                new_content, changed = update_xcode_created_by_header(
                    original_content,
                    author_name,
                    current_date,
                    scan_header_lines
                )

                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated_count += 1
                    print(f"✅ 更新文件头: {file_name}")
                else:
                    if 'Created by' not in '\n'.join(original_content.splitlines()[:int(scan_header_lines or 30)]):
                        no_header_count += 1

            except Exception as e:
                print(f"❌ 更新文件头失败 {file_name}: {e}")

    print(f"📊 文件头扫描: {scanned_count}")
    print(f"📊 文件头更新: {updated_count}")
    if no_header_count:
        print(f"ℹ️ 未找到 Created by 文件头: {no_header_count}")

    return updated_count


# ==================== JSON映射文件管理 ====================

def get_mapping_file_path(task_config):
    """根据项目路径生成映射文件名"""
    project_name = os.path.basename(task_config['project_path'].rstrip('/'))
    task_name = task_config.get('name', 'unnamed').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    mapping_filename = f"{project_name}_{task_name}_{timestamp}.json"
    return os.path.join(os.path.dirname(__file__), mapping_filename)

def save_mapping_to_json(mapping_dict, mapping_file, task_config):
    """保存映射关系到JSON文件"""
    mapping_data = {
        'timestamp': datetime.now().isoformat(),
        'task_config': task_config,
        'project_path': task_config['project_path'],
        'target_folder': task_config['target_folder'],
        'pbxproj_path': task_config['pbxproj_path'],
        'only_modify_prefix': task_config['only_modify_prefix'],
        'input_mapping_file': task_config.get('input_mapping_file', ''),
        'output_mapping_file': task_config.get('output_mapping_file', ''),
        'rollback_mapping_file': task_config.get('rollback_mapping_file', ''),
        'mapping': mapping_dict
    }
    
    mapping_dir = os.path.dirname(os.path.abspath(mapping_file))
    if mapping_dir and not os.path.exists(mapping_dir):
        os.makedirs(mapping_dir, exist_ok=True)

    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, ensure_ascii=False, indent=2)
    
    print(f"📋 映射文件已保存: {mapping_file}")

def load_mapping_from_json(mapping_file):
    """从JSON文件加载映射关系"""
    if not os.path.exists(mapping_file):
        print(f"❌ 映射文件不存在: {mapping_file}")
        return None
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)
    
    return mapping_data

def extract_mapping_dict(mapping_data):
    """兼容不同 JSON 结构，提取真正的 old -> new 映射字典"""
    if not mapping_data:
        return {}

    # 当前脚本保存的结构：{"mapping": {"OldClass": "NewClass"}}
    if isinstance(mapping_data, dict) and isinstance(mapping_data.get('mapping'), dict):
        return mapping_data.get('mapping') or {}

    # 兼容直接保存成 {"OldClass": "NewClass"} 的旧文件
    if isinstance(mapping_data, dict):
        metadata_keys = {
            'timestamp', 'task_config', 'project_path', 'target_folder',
            'pbxproj_path', 'only_modify_prefix', 'mapping', 'input_mapping_file', 'output_mapping_file', 'rollback_mapping_file'
        }
        return {k: v for k, v in mapping_data.items()
                if k not in metadata_keys and isinstance(k, str) and isinstance(v, str)}

    return {}

def normalize_mapping_files(mapping_files):
    """mapping_file 支持字符串或 list，这里统一转成路径数组"""
    if not mapping_files:
        return []
    if isinstance(mapping_files, str):
        return [mapping_files] if mapping_files.strip() else []
    if isinstance(mapping_files, (list, tuple)):
        return [str(p) for p in mapping_files if str(p).strip()]
    return []

def get_input_mapping_files(task_config):
    """获取用于复用旧映射的输入 mapping 文件。支持字符串或 list，并兼容旧字段。"""
    mapping_file = task_config.get('input_mapping_file', '')
    if mapping_file:
        return mapping_file

    # 兼容旧版配置
    if task_config.get('previous_mapping_file', ''):
        return task_config.get('previous_mapping_file', '')
    if task_config.get('mapping_file', ''):
        return task_config.get('mapping_file', '')
    return ''

def get_output_mapping_file(task_config):
    """获取当前任务输出 mapping 文件路径；未配置时自动生成带时间戳的文件。"""
    output_file = task_config.get('output_mapping_file', '')
    if isinstance(output_file, str) and output_file.strip():
        return output_file

    # 兼容旧版配置：如果只配置 mapping_file，也允许作为输出路径。
    mapping_file = task_config.get('mapping_file', '')
    if isinstance(mapping_file, str) and mapping_file.strip() and not task_config.get('input_mapping_file'):
        return mapping_file

    return get_mapping_file_path(task_config)

def get_rollback_mapping_file(task_config):
    """获取回滚用 mapping 文件路径，优先 rollback_mapping_file，兼容旧字段。"""
    for key in ('rollback_mapping_file', 'output_mapping_file', 'mapping_file', 'input_mapping_file', 'previous_mapping_file'):
        value = task_config.get(key, '')
        if isinstance(value, str) and value.strip():
            return value
        if isinstance(value, (list, tuple)) and value:
            candidates = [str(p) for p in value if str(p).strip()]
            if candidates:
                return candidates[-1]
    return ''

def is_mapping_reuse_enabled(task_config):
    """是否启用旧映射复用。优先使用 use_mapping_reuse；兼容 use_previous_mapping。"""
    if 'use_mapping_reuse' in task_config:
        return bool(task_config.get('use_mapping_reuse'))
    return bool(task_config.get('use_previous_mapping', False))

def load_previous_mapping_for_rename(task_config):
    """正常混淆模式下加载旧映射，用于复用旧类名映射"""
    if not is_mapping_reuse_enabled(task_config):
        return {}

    mapping_files = normalize_mapping_files(get_input_mapping_files(task_config))
    if not mapping_files:
        print("ℹ️ 已开启旧映射复用，但 input_mapping_file 为空，本次将全部重新生成")
        return {}

    previous_mapping = {}
    for mapping_file in mapping_files:
        if not os.path.exists(mapping_file):
            print(f"⚠️ 旧映射文件不存在，跳过: {mapping_file}")
            continue

        mapping_data = load_mapping_from_json(mapping_file)
        mapping_dict = extract_mapping_dict(mapping_data)
        if not mapping_dict:
            print(f"⚠️ 旧映射文件没有可用 mapping，跳过: {mapping_file}")
            continue

        # 后面的文件可以覆盖前面的文件，便于你按版本逐步叠加
        previous_mapping.update(mapping_dict)
        print(f"✅ 已加载旧映射: {mapping_file}，数量: {len(mapping_dict)}")

    if previous_mapping:
        print(f"📌 本任务可复用旧映射总数: {len(previous_mapping)}")

    return previous_mapping

def can_reuse_mapped_name(old_class_name, mapped_class_name, existing_classes, assigned_names):
    """检查旧映射名是否可以安全复用"""
    if not mapped_class_name:
        return False, "旧映射为空"

    # 与目标文件夹外的现有类冲突，不能复用，否则会重名
    if mapped_class_name in existing_classes:
        return False, f"旧映射名与目标目录外现有类冲突: {mapped_class_name}"

    # 本次任务里两个旧类映射成同一个新类，不能复用
    if mapped_class_name in assigned_names:
        return False, f"旧映射名在本次任务中重复: {mapped_class_name}"

    return True, ""

def rollback_from_mapping(mapping_file, task_config):
    """根据映射文件回滚重命名操作"""
    print(f"🔄 开始回滚操作...")
    print(f"📂 映射文件: {mapping_file}")
    
    mapping_data = load_mapping_from_json(mapping_file)
    if not mapping_data:
        return
    
    # 优先使用当前任务/GUI 传入的路径（便于对拷贝工程如 VivenHealth2 回滚）；
    # 未填时才回退到 mapping JSON 里保存的原路径。
    cfg_project = (task_config.get('project_path') or '').strip()
    cfg_pbx = (task_config.get('pbxproj_path') or '').strip()
    json_project = (mapping_data.get('project_path') or '').strip()
    json_pbx = (mapping_data.get('pbxproj_path') or '').strip()

    saved_project_path = cfg_project or json_project

    if cfg_pbx and os.path.exists(cfg_pbx):
        saved_pbxproj_path = cfg_pbx
    elif cfg_project:
        # GUI 指定了新工程树时，不要沿用 JSON 里旧工程的 pbxproj；
        # 且忽略 _build_task_configs 可能误填的不存在路径（如 Sources.xcodeproj）
        saved_pbxproj_path = guess_pbxproj_path(cfg_project)
        if cfg_pbx and cfg_pbx != saved_pbxproj_path:
            print(f"⚠️ 配置中的 pbxproj 不存在或不可用: {cfg_pbx}")
            print(f"ℹ️ 已改用自动推导: {saved_pbxproj_path}")
    else:
        if json_pbx and os.path.exists(json_pbx):
            saved_pbxproj_path = json_pbx
        else:
            saved_pbxproj_path = guess_pbxproj_path(saved_project_path)

    if json_project and cfg_project and os.path.abspath(json_project) != os.path.abspath(cfg_project):
        print(f"ℹ️ mapping 内原路径: {json_project}")
        print(f"ℹ️ 已改用当前 project_path: {cfg_project}")

    print(f"📂 项目路径: {saved_project_path}")
    print(f"📂 pbxproj路径: {saved_pbxproj_path}")
    
    mapping_dict = extract_mapping_dict(mapping_data)
    reverse_mapping = {v: k for k, v in mapping_dict.items()}
    
    print(f"📋 共有 {len(reverse_mapping)} 个类需要回滚")
    
    # 第一步：回滚文件名
    rollback_count = 0
    for (root, dirs, files) in os.walk(saved_project_path):
        for file_name in files:
            if file_name.endswith(suf_set):
                file_path = os.path.join(root, file_name)
                old_class_name = os.path.splitext(file_name)[0]
                
                if old_class_name in reverse_mapping:
                    original_name = reverse_mapping[old_class_name]
                    new_filename = file_rename(file_path, old_class_name, original_name)
                    if new_filename:
                        print(f"✅ 回滚文件: {old_class_name} -> {original_name}")
                        rollback_count += 1
    
    # 第二步：回滚文件内容引用
    updated_files = 0
    for (root, dirs, files) in os.walk(saved_project_path):
        for file_name in files:
            if file_name.endswith(suf_set):
                file_path = os.path.join(root, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    content_modified = False
                    for new_class, old_class in reverse_mapping.items():
                        if new_class in content:
                            content = replace_with_header_protection(content, new_class, old_class)
                            content_modified = True
                    
                    if content_modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files += 1
                
                except Exception as e:
                    print(f"❌ 回滚文件内容失败 {file_name}: {e}")
    
    # 第三步：回滚 project.pbxproj
    try:
        if os.path.exists(saved_pbxproj_path):
            with open(saved_pbxproj_path, 'r', encoding='utf-8') as f:
                pbx_content = f.read()
            
            pbx_modified = False
            # 长名优先，避免短名误伤
            pairs = sorted(reverse_mapping.items(), key=lambda kv: len(kv[0]), reverse=True)
            for new_class, old_class in pairs:
                for ext in suf_set:
                    new_filename = new_class + ext
                    old_filename = old_class + ext
                    if new_filename in pbx_content:
                        pbx_content = pbx_content.replace(new_filename, old_filename)
                        pbx_modified = True
                # 少数引用可能不含扩展名（极少见）；仅当两侧都是完整标识时替换
                if new_class in pbx_content:
                    pbx_content = pbx_content.replace(new_class, old_class)
                    pbx_modified = True
            
            if pbx_modified:
                with open(saved_pbxproj_path, 'w', encoding='utf-8') as f:
                    f.write(pbx_content)
                print("✅ project.pbxproj 回滚完成")
            else:
                print("ℹ️ project.pbxproj 中未发现需回滚的文件名引用")
        else:
            print(f"⚠️ project.pbxproj 文件不存在: {saved_pbxproj_path}")
    
    except Exception as e:
        print(f"❌ project.pbxproj 回滚失败: {e}")
    
    print(f"\n🎉 回滚完成!")
    print(f"📊 回滚文件数: {rollback_count}")
    print(f"📊 更新引用文件数: {updated_files}")

# ==================== 核心功能函数 ====================

def collect_existing_class_names(project_path, exclude_folder=None):
    """
    收集项目中所有现有的类名（不包括将要重命名的类）
    返回一个set，包含所有现有类名
    """
    existing_classes = set()
    
    print("🔍 扫描项目中现有的类名...")
    
    for (root, dirs, files) in os.walk(project_path):
        for file_name in files:
            if file_name.endswith(suf_set):
                file_path = os.path.join(root, file_name)
                
                # 如果指定了排除文件夹，跳过该文件夹内的文件
                # （因为这些文件将要被重命名）
                if exclude_folder:
                    abs_exclude = os.path.abspath(exclude_folder)
                    abs_file = os.path.abspath(file_path)
                    try:
                        common = os.path.commonpath([abs_exclude, abs_file])
                        if common == abs_exclude:
                            continue  # 跳过目标文件夹内的文件
                    except Exception:
                        pass
                
                class_name = os.path.splitext(file_name)[0]
                existing_classes.add(class_name)
    
    print(f"📊 发现 {len(existing_classes)} 个现有类名")
    return existing_classes

def sanitize_identifier_component(raw_word):
    """清洗中间词，去除非法字符并转为驼峰"""
    parts = re.split(r'[^A-Za-z0-9]+', raw_word.strip())
    parts = [p for p in parts if p]
    if not parts:
        return 'Name'
    tokens = []
    camel_pattern = r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+'
    for part in parts:
        subs = re.findall(camel_pattern, part)
        for s in subs:
            if s.isdigit():
                tokens.append(s)
            elif len(s) >= 2 and s.isupper():
                tokens.append(s)
            else:
                tokens.append(s[:1].upper() + s[1:].lower())
    camel = ''.join(tokens)
    if not re.match(r'[A-Za-z]', camel):
        camel = 'N' + camel
    return camel

def parse_class_name(class_name, suffix_config, task_config):
    """解析类名为前缀、中间、后缀三部分"""
    matched_prefix = None
    for prefix in task_config['old_prefixes']:
        if class_name.startswith(prefix):
            matched_prefix = prefix
            break
    
    if not matched_prefix:
        return None, None, None
    
    if task_config['only_modify_prefix']:
        remaining_part = class_name[len(matched_prefix):]
        return matched_prefix, remaining_part, ""
    
    matched_suffix = None
    for suffix in suffix_config['old_suffixes']:
        if class_name.endswith(suffix):
            matched_suffix = suffix
            break
    
    if not matched_suffix:
        return None, None, None
    
    middle_part = class_name[len(matched_prefix):-len(matched_suffix)]
    return matched_prefix, middle_part, matched_suffix

def generate_middle_name(used_names, max_retries=100):
    """生成唯一的中间名称，支持去重重试"""
    for attempt in range(max_retries):
        word_count = random.randint(2, 3)
        selected_words = []
        
        available_groups = random.sample(middle_word_groups, min(word_count, len(middle_word_groups)))
        
        for group in available_groups:
            word = random.choice(group)
            sanitized_word = sanitize_identifier_component(word)
            selected_words.append(sanitized_word)
        
        # 如果词数不够，补充额外单词
        if len(selected_words) < word_count:
            all_remaining = []
            for group in middle_word_groups:
                for word in group:
                    sanitized = sanitize_identifier_component(word)
                    if sanitized not in selected_words:
                        all_remaining.append(sanitized)
            
            while len(selected_words) < word_count and all_remaining:
                additional = random.choice(all_remaining)
                selected_words.append(additional)
                all_remaining.remove(additional)
        
        random.shuffle(selected_words)
        middle_name = ''.join(selected_words)
        
        # 🆕 去重检查
        if middle_name not in used_names:
            return middle_name
        
        # 如果重复，尝试添加一个额外的随机单词
        if attempt < max_retries - 10:
            all_words = [sanitize_identifier_component(word)
                        for group in middle_word_groups
                        for word in group]
            extra_word = random.choice([w for w in all_words if w not in selected_words])
            middle_name_with_extra = middle_name + extra_word
            if middle_name_with_extra not in used_names:
                return middle_name_with_extra
    
    # 最后的兜底方案：使用版本号
    base_name = 'Generated'
    version = 2
    while f"{base_name}V{version}" in used_names:
        version += 1
    return f"{base_name}V{version}"

def generate_new_class_name(old_class_name, suffix_config, used_names, used_full_names, task_config, existing_classes=None):
    """
    生成新的类名，支持去重
    Args:
        old_class_name: 原类名
        suffix_config: 后缀配置
        used_names: 已使用的中间名集合
        used_full_names: 已使用的完整类名集合
        task_config: 任务配置
        existing_classes: 项目中现有的类名集合（用于冲突检测）
    """
    if existing_classes is None:
        existing_classes = set()
    
    old_prefix, middle_part, old_suffix = parse_class_name(old_class_name, suffix_config, task_config)
    
    if old_prefix is None:
        return None
    
    if task_config['only_modify_prefix']:
        max_attempts = 50
        for _ in range(max_attempts):
            new_prefix = random.choice(task_config['new_prefixes'])
            new_class_name = new_prefix + middle_part
            
            # 检查是否与现有类名冲突 + 本次生成的类名冲突
            if new_class_name not in existing_classes and new_class_name not in used_full_names:
                used_full_names.add(new_class_name)
                return new_class_name
        
        # 兜底：使用数字后缀
        new_prefix = random.choice(task_config['new_prefixes'])
        base_name = new_prefix + middle_part
        counter = 2
        while f"{base_name}{counter}" in existing_classes or f"{base_name}{counter}" in used_full_names:
            counter += 1
        final_name = f"{base_name}{counter}"
        used_full_names.add(final_name)
        print(f"⚠️  类名冲突，使用兜底方案: {old_class_name} -> {final_name}")
        return final_name
    
    if not all([old_prefix, middle_part, old_suffix]):
        return None
    
    # 支持完整类名去重（包括现有类名检测）
    max_attempts = 50
    new_class_name = ''
    for _ in range(max_attempts):
        new_middle = generate_middle_name(used_names)
        new_prefix = random.choice(task_config['new_prefixes'])
        new_suffix = random.choice(suffix_config['new_suffixes'])
        
        new_class_name = new_prefix + new_middle + new_suffix
        
        # 检查完整类名是否与现有类名冲突 + 本次生成的类名冲突
        if new_class_name not in existing_classes and new_class_name not in used_full_names:
            used_names.add(new_middle)
            used_full_names.add(new_class_name)
            return new_class_name
    
    # 兜底：添加数字后缀（确保不与现有类名冲突）
    base_name = new_class_name
    counter = 2
    while f"{base_name}{counter}" in existing_classes or f"{base_name}{counter}" in used_full_names:
        counter += 1
    final_name = f"{base_name}{counter}"
    used_full_names.add(final_name)
    print(f"⚠️  类名冲突，使用兜底方案: {old_class_name} -> {final_name}")
    return final_name

def file_rename(file_path, old_name, new_name):
    """文件重命名函数"""
    try:
        root_path = os.path.split(file_path)[0]
        root_file = os.path.split(file_path)[1]
        filename = os.path.splitext(root_file)[0]
        filetype = os.path.splitext(root_file)[1]
        
        new_filename = filename.replace(old_name, new_name)
        new_path = os.path.join(root_path, new_filename + filetype)
        
        os.renames(file_path, new_path)
        return new_filename
    except Exception as e:
        print(f"❌ 文件重命名失败 {file_path}: {e}")
        return None

def replace_with_header_protection(file_content, old_str, new_str):
    """保护文件头的替换函数，使用单词边界防止子串误替换"""
    lines = file_content.split('\n')
    result_lines = []
    in_header = True
    pattern = re.compile(r'\b' + re.escape(old_str) + r'\b')

    for line in lines:
        if in_header:
            stripped = line.strip()
            if stripped == '' or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                result_lines.append(line)
                continue
            else:
                in_header = False

        result_lines.append(pattern.sub(new_str, line))

    return '\n'.join(result_lines)

def is_in_target_folder(file_path, task_config):
    """检查文件是否在目标文件夹中"""
    abs_target = os.path.abspath(task_config['target_folder'])
    abs_file = os.path.abspath(file_path)
    if task_config['only_current_level']:
        return os.path.dirname(abs_file) == abs_target
    try:
        common = os.path.commonpath([abs_target, abs_file])
        return common == abs_target
    except Exception:
        return False

def validate_config(task_config):
    """验证配置的有效性"""
    print("🔍 验证配置...")
    
    if not os.path.exists(task_config['project_path']):
        print(f"❌ 项目路径不存在: {task_config['project_path']}")
        return False
    
    if not os.path.exists(task_config['target_folder']):
        print(f"❌ 目标文件夹不存在: {task_config['target_folder']}")
        return False
    
    if not task_config['old_prefixes']:
        print("❌ 旧前缀数组为空")
        return False

    if not task_config['new_prefixes']:
        print("❌ 新前缀数组为空")
        return False
    
    if not task_config['only_modify_prefix']:
        if not suffix_groups:
            print("❌ 后缀配置组为空")
            return False
        
        for group in suffix_groups:
            if not group.get('new_suffixes'):
                print(f"❌ 后缀组 '{group.get('name')}' 的新后缀为空")
                return False
        
        if not middle_word_groups:
            print("❌ 中间词库为空")
            return False
    
    print("✅ 配置验证通过")
    return True

# ==================== 主执行逻辑 ====================

def print_task_config(task_config):
    """打印任务配置信息"""
    print("📝 任务配置信息:")
    print(f"  - 任务名称: {task_config.get('name', '未命名')}")
    print(f"  - 运行模式: {'仅修改前缀' if task_config['only_modify_prefix'] else '完全重命名'}")
    print(f"  - 回滚模式: {'是' if task_config['rollback_mode'] else '否'}")
    print(f"  - 输入映射文件: {get_input_mapping_files(task_config) or '未指定'}")
    print(f"  - 输出映射文件: {get_output_mapping_file(task_config) or '自动生成'}")
    print(f"  - 回滚映射文件: {get_rollback_mapping_file(task_config) or '未指定'}")
    if not task_config['rollback_mode']:
        print(f"  - 复用旧映射: {'是' if is_mapping_reuse_enabled(task_config) else '否'}")
    print(f"  - 只处理当前层: {'是' if task_config['only_current_level'] else '否'}")
    print(f"  - 目标文件夹: {task_config['target_folder']}")
    print(f"  - 旧前缀: {task_config['old_prefixes']}")
    print(f"  - 新前缀: {task_config['new_prefixes']}")
    print(f"  - 项目路径: {task_config['project_path']}")
    print(f"  - pbxproj路径: {task_config['pbxproj_path']}")
    header_config = get_copyright_header_config(task_config)
    print(f"  - 文件头版权信息: {'开启' if header_config.get('enabled') else '关闭'}")
    if header_config.get('enabled'):
        print(f"  - 文件头作者: {header_config.get('author_name', '')}")
        print(f"  - 文件头范围: {header_config.get('scope', 'target_folder')}")

def main(task_config):
    """执行单个任务"""
    print("🚀 工具启动（整合版：V2.5 mapping + V2.3 文件头）")
    print("-" * 70)
    print_task_config(task_config)
    print("-" * 70)
    
    if not task_config['only_modify_prefix']:
        print(f"📋 后缀配置组数: {len(suffix_groups)}")
        for group in suffix_groups:
            print(f"  - {group['name']}: {group['old_suffixes']} -> {group['new_suffixes']}")
    
    print("-" * 70)
    
    if not validate_config(task_config):
        return

    # 读取旧映射：正常混淆时优先复用，新增类才重新生成
    previous_mapping = load_previous_mapping_for_rename(task_config)
    reserved_previous_names = set(previous_mapping.values())
    assigned_names = set()
    reused_mapping_count = 0
    new_mapping_count = 0
    conflict_mapping_count = 0
    
    # 合并所有后缀配置
    all_old_suffixes = []
    all_new_suffixes = []
    for group in suffix_groups:
        all_old_suffixes.extend(group['old_suffixes'])
        all_new_suffixes.extend(group['new_suffixes'])
    
    # 去重
    all_old_suffixes = list(set(all_old_suffixes))
    all_new_suffixes = list(set(all_new_suffixes))
    
    used_middle_names = set()
    used_full_names = set()
    needModifyDic = {}

    # 提前锁定所有旧映射目标名，防止新生成的名字与历史混淆名重复
    if previous_mapping:
        used_full_names.update(reserved_previous_names)

    project_path = task_config['project_path']
    target_folder = task_config['target_folder']
    pbxproj_path = (task_config.get('pbxproj_path') or '').strip()
    if not pbxproj_path or not os.path.exists(pbxproj_path):
        guessed = guess_pbxproj_path(task_config.get('project_path') or '')
        if guessed and guessed != pbxproj_path:
            print(f'⚠️ pbxproj 无效: {pbxproj_path or "(空)"} → 改用 {guessed}')
        pbxproj_path = guessed
        task_config['pbxproj_path'] = pbxproj_path
    
    # 收集项目中现有的类名（排除目标文件夹）
    existing_classes = collect_existing_class_names(project_path, target_folder)
    
    print("📋 扫描需要重命名的文件...")
    renamed_count = 0
    
    for (root, dirs, files) in os.walk(project_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            if not is_in_target_folder(file_path, task_config):
                continue
            
            if file_name.endswith(suf_set):
                old_class_name = os.path.splitext(file_name)[0]
                
                # 匹配后缀组；prefix-only 模式不依赖后缀，用第一个组判断前缀即可
                if task_config['only_modify_prefix']:
                    dummy = suffix_groups[0] if suffix_groups else {'old_suffixes': [], 'new_suffixes': []}
                    matched_group = dummy if parse_class_name(old_class_name, dummy, task_config)[0] else None
                else:
                    matched_group = None
                    for group in suffix_groups:
                        if parse_class_name(old_class_name, group, task_config)[0]:
                            matched_group = group
                            break
                
                if matched_group:
                    if old_class_name in needModifyDic:
                        new_class_name = needModifyDic[old_class_name]
                    else:
                        # ✅ 优先复用上一版本映射；如果没有旧映射或旧映射冲突，则重新生成
                        mapped_class_name = previous_mapping.get(old_class_name)
                        if mapped_class_name:
                            can_reuse, reason = can_reuse_mapped_name(
                                old_class_name,
                                mapped_class_name,
                                existing_classes,
                                assigned_names
                            )
                            if can_reuse:
                                new_class_name = mapped_class_name
                                used_full_names.add(new_class_name)  # 防止后续生成与复用名重复
                                reused_mapping_count += 1
                                print(f"♻️ 复用旧映射: {old_class_name} -> {new_class_name}")
                            else:
                                conflict_mapping_count += 1
                                print(f"⚠️ 旧映射不可复用: {old_class_name} -> {mapped_class_name}，原因: {reason}，将重新生成")
                                new_class_name = generate_new_class_name(
                                    old_class_name,
                                    matched_group,
                                    used_middle_names,
                                    used_full_names,
                                    task_config,
                                    existing_classes
                                )
                                if new_class_name:
                                    new_mapping_count += 1
                        else:
                            # 新增类
                            new_class_name = generate_new_class_name(
                                old_class_name,
                                matched_group,
                                used_middle_names,
                                used_full_names,
                                task_config,
                                existing_classes
                            )
                            if new_class_name:
                                new_mapping_count += 1

                        if new_class_name:
                            needModifyDic[old_class_name] = new_class_name
                            assigned_names.add(new_class_name)
                    
                    if new_class_name:
                        new_filename = file_rename(file_path, old_class_name, new_class_name)
                        if new_filename:
                            print(f"✅ {old_class_name} -> {new_class_name}")
                            renamed_count += 1
    
    if renamed_count == 0:
        print("ℹ️ 没有找到需要重命名的文件")
        header_updated_count = update_task_file_headers(task_config)
        print("\n" + "="*70)
        print(f"🎉 任务 [{task_config.get('name', '未命名')}] 完成!")
        print(f"📊 重命名文件: {renamed_count}")
        print(f"📊 文件头更新: {header_updated_count}")
        print("="*70)
        return
    
    print(f"\n📊 共重命名 {renamed_count} 个文件")
    print(f"📊 复用旧映射: {reused_mapping_count}")
    print(f"📊 新生成映射: {new_mapping_count}")
    if conflict_mapping_count > 0:
        print(f"📊 旧映射冲突后重新生成: {conflict_mapping_count}")
    
    # 保存映射文件：优先保存到 output_mapping_file；未配置则自动生成
    mapping_file = get_output_mapping_file(task_config)
    save_mapping_to_json(needModifyDic, mapping_file, task_config)
    
    # 更新文件引用
    print(f"\n🔄 更新项目中的类名引用...")
    updated_files_count = 0
    
    for (root, dirs, files) in os.walk(project_path):
        for file_name in files:
            if file_name.endswith(suf_set):
                file_path = os.path.join(root, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    content_modified = False
                    current_content = original_content
                    
                    for old_class, new_class in needModifyDic.items():
                        if old_class in current_content:
                            current_content = replace_with_header_protection(current_content, old_class, new_class)
                            content_modified = True
                    
                    if content_modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(current_content)
                        updated_files_count += 1
                
                except Exception as e:
                    print(f"❌ 处理文件失败 {file_name}: {e}")
    
    print(f"📊 共更新了 {updated_files_count} 个文件")
    
    # 更新 project.pbxproj
    print(f"\n🔧 更新 project.pbxproj...")
    try:
        if os.path.exists(pbxproj_path):
            with open(pbxproj_path, 'r', encoding='utf-8') as f:
                pbx_content = f.read()
            
            pbx_modified = False
            for old_class, new_class in needModifyDic.items():
                for ext in suf_set:
                    old_filename = old_class + ext
                    new_filename = new_class + ext
                    if old_filename in pbx_content:
                        pbx_content = pbx_content.replace(old_filename, new_filename)
                        pbx_modified = True
            
            if pbx_modified:
                with open(pbxproj_path, 'w', encoding='utf-8') as f:
                    f.write(pbx_content)
                print("✅ project.pbxproj 更新完成")
    
    except Exception as e:
        print(f"❌ project.pbxproj 更新失败: {e}")
    
    # 更新 Xcode 文件头版权信息（V2.3）
    header_updated_count = update_task_file_headers(task_config)

    print("\n" + "="*70)
    print(f"🎉 任务 [{task_config.get('name', '未命名')}] 完成!")
    print(f"📊 重命名文件: {renamed_count}")
    print(f"📊 复用旧映射: {reused_mapping_count}")
    print(f"📊 新生成映射: {new_mapping_count}")
    print(f"📊 更新引用: {updated_files_count}")
    print(f"📊 文件头更新: {header_updated_count}")
    print(f"📋 映射文件: {mapping_file}")
    print(f"\n💡 回滚方法:")
    print(f"   1. 在对应任务配置中设置 'rollback_mode': True")
    print(f"   2. 设置 'rollback_mapping_file': '{mapping_file}'")
    print(f"   3. 重新运行脚本")
    print("="*70)

def apply_external_config(config_obj):
    """从 GUI / CLI JSON 覆盖 PROJECT_CONFIG、COPYRIGHT_HEADER_CONFIG、任务列表、词库"""
    global PROJECT_CONFIG, COPYRIGHT_HEADER_CONFIG, TASK_CONFIGS_RAW, TASK_CONFIGS, _P
    global middle_word_groups, suffix_groups

    if not isinstance(config_obj, dict):
        raise ValueError("config 必须是 JSON object")

    # GUI / JSON 可选覆盖中间词库与后缀组；缺省则保留脚本内默认
    mwg = config_obj.get('middle_word_groups')
    if isinstance(mwg, list) and mwg:
        # 期望 [[str, ...], [str, ...], ...]
        cleaned = []
        for group in mwg:
            if isinstance(group, list):
                words = [str(w).strip() for w in group if str(w).strip()]
                if words:
                    cleaned.append(words)
        if cleaned:
            middle_word_groups = cleaned
            print(f"📦 已从配置加载 middle_word_groups（{len(cleaned)} 组，共 {sum(len(g) for g in cleaned)} 词）")

    sg = config_obj.get('suffix_groups')
    if isinstance(sg, list) and sg:
        suffix_groups = sg
        print(f"📦 已从配置加载 suffix_groups（{len(sg)} 组）")

    project_cfg = config_obj.get('project_config') or {}
    if config_obj.get('project_path'):
        project_cfg = dict(project_cfg)
        project_cfg['project_path'] = config_obj['project_path']
    if config_obj.get('maps_dir'):
        project_cfg = dict(project_cfg)
        project_cfg['maps_dir'] = config_obj['maps_dir']
    if project_cfg:
        PROJECT_CONFIG.update(project_cfg)

    header_cfg = config_obj.get('copyright_header') or config_obj.get('copyright_header_config')
    if isinstance(header_cfg, dict):
        COPYRIGHT_HEADER_CONFIG.update(header_cfg)
    elif header_cfg is False:
        COPYRIGHT_HEADER_CONFIG['enabled'] = False

    defaults = config_obj.get('task_defaults')
    if isinstance(defaults, dict):
        TASK_DEFAULTS.update(defaults)

    tasks = config_obj.get('tasks') or config_obj.get('task_configs') or config_obj.get('TASK_CONFIGS_RAW')
    if tasks:
        TASK_CONFIGS_RAW = list(tasks)
        _P = PROJECT_CONFIG['project_path']
        TASK_CONFIGS = _build_task_configs()
        # 把全局 copyright 注入每个任务（任务级可再覆盖）
        for t in TASK_CONFIGS:
            if 'copyright_header_config' not in t and COPYRIGHT_HEADER_CONFIG.get('enabled'):
                t['copyright_header_config'] = dict(COPYRIGHT_HEADER_CONFIG)
    else:
        # 无 tasks 时仍重建，以便使用新的 project_path
        _P = PROJECT_CONFIG['project_path']
        TASK_CONFIGS = _build_task_configs()
        for t in TASK_CONFIGS:
            if 'copyright_header_config' not in t and COPYRIGHT_HEADER_CONFIG.get('enabled'):
                t['copyright_header_config'] = dict(COPYRIGHT_HEADER_CONFIG)

    return TASK_CONFIGS


def run_all_tasks(task_list):
    if not task_list:
        print("❌ 任务配置列表为空，请在配置中添加 tasks")
        return 1

    total_tasks = len(task_list)
    print(f"🚀 共有 {total_tasks} 个任务待执行")
    print("=" * 70)

    for idx, task_config in enumerate(task_list, 1):
        print(f"\n{'#' * 70}")
        print(f"# 任务 {idx}/{total_tasks}: {task_config.get('name', '未命名')}")
        print(f"{'#' * 70}\n")

        if task_config.get('rollback_mode', False):
            rollback_file = get_rollback_mapping_file(task_config)
            if not rollback_file:
                print(f"❌ 任务 [{task_config.get('name')}] 的 rollback_mapping_file 未指定")
            else:
                rollback_from_mapping(rollback_file, task_config)
        else:
            main(task_config)

        print("\n")

    print("=" * 70)
    print(f"🎊 全部 {total_tasks} 个任务执行完毕!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="iOS 类名混淆整合脚本（V2.5 + V2.3 文件头）")
    parser.add_argument("--config", "-c", help="JSON 配置文件路径（由可视化工具生成）")
    parser.add_argument("--dry-print-config", action="store_true", help="仅打印解析后的任务配置后退出")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        apply_external_config(cfg)
        print(f"📥 已加载配置: {args.config}")

    if args.dry_print_config:
        for t in TASK_CONFIGS:
            print_task_config(t)
            print("-" * 40)
        sys.exit(0)

    sys.exit(run_all_tasks(TASK_CONFIGS) or 0)

