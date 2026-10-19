import os
import re
import random
import json
from datetime import datetime

# ==================== 任务配置区域 ====================









# 🆕 文件头版权信息配置
# 功能：把 Xcode 文件头里的 “Created by xxx on 2025/3/6.” 自动改成指定作者 + 当前日期。
# 例如：//  Created by LiXiang on 2026/7/8.
COPYRIGHT_HEADER_CONFIG = {
    'enabled': True,                  # True: 开启文件头版权信息更新 / False: 关闭
    'author_name': 'VivenApp',             # ✅ 在这里填写 Created by 后面的名称
    'scope': 'project',         # target_folder: 只处理目标目录 / project: 处理整个项目路径
    'scan_header_lines': 30,          # 只扫描文件开头前 N 行，避免误改正文里的 Created by
}


# 任务配置列表 - 按顺序执行每个任务
TASK_CONFIGS = [


#                {
#                'name': '任务1-全局模块',                # 任务名称（用于日志标识）
#                'only_modify_prefix': True,            # True: 只替换前缀 / False: 完全重命名
#                'rollback_mode': False,                 # True: 回滚模式 / False: 重命名模式
#                'rollback_mapping_file': '/Users/qc/Desktop/未命名文件夹/NDSTPP_任务1-全局模块.json',  # 回滚时的映射文件路径
#                'only_current_level': False,            # True: 只处理当前层 / False: 包含子目录
#                'old_prefixes': ['HR'],
#                'new_prefixes': ['VEH'],
#                'target_folder': '/Volumes/D/appSpace/VivenHealthApp/VivenHealth/VivenHealth/Sources',
#                'project_path': '/Volumes/D/appSpace/VivenHealthApp/VivenHealth/VivenHealth/Sources',
#                'pbxproj_path': '/Volumes/D/appSpace/VivenHealthApp/VivenHealth/VivenHealth.xcodeproj/project.pbxproj',
#                },
                
            
                # 可继续添加更多任务配置
                {
                'name': '任务2-全局模块',                # 任务名称（用于日志标识）
                'only_modify_prefix': False,            # True: 只替换前缀 / False: 完全重命名
                'rollback_mode': False,                 # True: 回滚模式 / False: 重命名模式
                'rollback_mapping_file': '/Volumes/SSD1TB/Widget/DevTool/Rename/HITIRING_任务2-全局模块_20260525_151845.json',            # 回滚时的映射文件路径
                'only_current_level': False,            # True: 只处理当前层 / False: 包含子目录
                'old_prefixes': ['VEH'],
                'new_prefixes': ['VEH'],
                 'target_folder': '/Volumes/D/appSpace/VivenHealthApp/VivenHealth/VivenHealth/Sources',
                'project_path': '/Volumes/D/appSpace/VivenHealthApp/VivenHealth/VivenHealth/Sources',
                'pbxproj_path': '/Volumes/D/appSpace/VivenHealthApp/VivenHealth/VivenHealth.xcodeproj/project.pbxproj',
                },
##                
#                {
#                'name': '任务3-全局模块',                # 任务名称（用于日志标识）
#                'only_modify_prefix': False,            # True: 只替换前缀 / False: 完全重命名
#                'rollback_mode': False,                 # True: 回滚模式 / False: 重命名模式
#                'rollback_mapping_file': '/Users/qc/Desktop/未命名文件夹/NDSTPP_任务3-全局模块.json',            # 回滚时的映射文件路径
#                'only_current_level': False,            # True: 只处理当前层 / False: 包含子目录
#                'old_prefixes': ['HR'],
#                'new_prefixes': ['HR'],
#                'target_folder': '/Volumes/SSD1TB/AppStore/NexusRing/NexusRing',
#                'project_path': '/Volumes/SSD1TB/AppStore/NexusRing/NexusRing',
#                'pbxproj_path': '/Volumes/SSD1TB/AppStore/NexusRing/NexusRing.xcodeproj/project.pbxproj',
#                }
                ]

# 🆕 多组后缀配置 - 支持一次运行处理多种后缀类型
suffix_groups = [
                 {
                 'name': 'Controller',
                 'old_suffixes': ['Controller', 'ViewController', 'Ctrl', 'VC'],
                 'new_suffixes': ['VC', 'ViewController', 'ViewCtrl']
                 },
                 {
                 'name': 'ViewModel',
                 'old_suffixes': ['ViewModel', 'Manager', 'Info', 'VM'],
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


# 中间词库（三组单词）
middle_word_groups = [
                      # Group 1 - 实体词：传感、光影、材质、形态与智能硬件意象
                      [
                       'Gyrosa', 'Optiqa', 'Alloyx', 'Facet',  'Prismi', 'Beaml',
                       'Glowra', 'Pulvex', 'Thermi', 'Magniq', 'Axial',  'Nodrix',
                       'Shella', 'Cerami', 'Silvex', 'Flecta', 'Morpho', 'Curvix',
                       'Edgeon', 'Rayvex', 'Glimra', 'Lucion', 'Halove', 'Sphera',
                       'Orbita', 'Fibron', 'Tensiq', 'Vistro', 'Auralo', 'Vibrax'
                       ],
                      
                      # Group 2 - 架构词：连接、节点、数据流、通信与设备协同
                      [
                       'Syncra', 'Bondix', 'Pairon', 'Meshra', 'Hubvex', 'Busion',
                       'Pathiq', 'Routex', 'Porton', 'Fluxiq', 'Bridgo', 'Nexion',
                       'Coreon', 'Dockra', 'Uplinx', 'Packon', 'Cachex', 'Muxora',
                       'Gateon', 'Chaina', 'Bindra', 'Tunela', 'Pivot',  'Loopra',
                       'Peeron', 'Clust',  'Shard',  'Relixo', 'Pathix', 'Netora'
                       ],
                      
                      # Group 3 - 功能词：语音、交互、状态与智能体验
                      [
                       'Tonova', 'Audvex', 'Vocalx', 'Phonix', 'Notion', 'Memoix',
                       'Logvex', 'Markon', 'Tagvex', 'Tracix', 'Scenra', 'Briefx',
                       'Echoza', 'Dialox', 'Phras',  'Timvex', 'Moment', 'Clipra',
                       'Frameo', 'Remind', 'Hearon', 'Talkon', 'Voceon', 'Summix',
                       'Statix', 'Agilix', 'Calmra', 'Readyx', 'Flowra', 'Clearo'
                       ]
                      ]

# 支持的文件类型
suf_set = ('.h', '.m', '.swift')


# ==================== 文件头版权信息处理 ====================

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

    # 兼容：// Created by xxx on 2025/3/6. / //  Created by xxx on 2025-03-06.
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
                    # 没匹配到 Created by 行也不报错，避免影响重命名流程
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
        'mapping': mapping_dict
    }
    
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

def rollback_from_mapping(mapping_file, task_config):
    """根据映射文件回滚重命名操作"""
    print(f"🔄 开始回滚操作...")
    print(f"📂 映射文件: {mapping_file}")
    
    mapping_data = load_mapping_from_json(mapping_file)
    if not mapping_data:
        return
    
    # 使用映射文件中保存的路径
    saved_project_path = mapping_data.get('project_path', task_config['project_path'])
    saved_pbxproj_path = mapping_data.get('pbxproj_path', task_config['pbxproj_path'])
    
    print(f"📂 项目路径: {saved_project_path}")
    print(f"📂 pbxproj路径: {saved_pbxproj_path}")
    
    reverse_mapping = {v: k for k, v in mapping_data['mapping'].items()}
    
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
            for new_class, old_class in reverse_mapping.items():
                for ext in suf_set:
                    new_filename = new_class + ext
                    old_filename = old_class + ext
                    if new_filename in pbx_content:
                        pbx_content = pbx_content.replace(new_filename, old_filename)
                        pbx_modified = True
            
            if pbx_modified:
                with open(saved_pbxproj_path, 'w', encoding='utf-8') as f:
                    f.write(pbx_content)
                print("✅ project.pbxproj 回滚完成")
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
        for attempt in range(max_attempts):
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
    for attempt in range(max_attempts):
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
    """保护文件头的替换函数"""
    lines = file_content.split('\n')
    result_lines = []
    in_header = True
    
    for line in lines:
        if in_header:
            stripped = line.strip()
            if stripped.startswith('//') or stripped == '':
                result_lines.append(line)
                continue
            else:
                in_header = False
        
        result_lines.append(line.replace(old_str, new_str))
    
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
    if task_config['rollback_mode']:
        print(f"  - 回滚映射文件: {task_config.get('rollback_mapping_file', '未指定')}")
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
    print("🚀 工具启动（增强版 v1.5）")
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
    
    project_path = task_config['project_path']
    target_folder = task_config['target_folder']
    pbxproj_path = task_config['pbxproj_path']
    
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
                
                # 尝试匹配所有后缀组
                matched_group = None
                for group in suffix_groups:
                    parsed = parse_class_name(old_class_name, group, task_config)
                    if parsed[0]:
                        matched_group = group
                        break
                
                if matched_group:
                    if old_class_name in needModifyDic:
                        new_class_name = needModifyDic[old_class_name]
                    else:
                        new_class_name = generate_new_class_name(
                            old_class_name,
                            matched_group,
                            used_middle_names,
                            used_full_names,
                            task_config,
                            existing_classes
                        )
                        if new_class_name:
                            needModifyDic[old_class_name] = new_class_name
                    
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
    
    # 保存映射文件
    mapping_file = get_mapping_file_path(task_config)
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
    
    # 更新 Xcode 文件头版权信息
    header_updated_count = update_task_file_headers(task_config)
    
    print("\n" + "="*70)
    print(f"🎉 任务 [{task_config.get('name', '未命名')}] 完成!")
    print(f"📊 重命名文件: {renamed_count}")
    print(f"📊 更新引用: {updated_files_count}")
    print(f"📊 文件头更新: {header_updated_count}")
    print(f"📋 映射文件: {mapping_file}")
    print(f"\n💡 回滚方法:")
    print(f"   1. 在对应任务配置中设置 'rollback_mode': True")
    print(f"   2. 设置 'rollback_mapping_file': '{mapping_file}'")
    print(f"   3. 重新运行脚本")
    print("="*70)

if __name__ == "__main__":
    if not TASK_CONFIGS:
        print("❌ 任务配置列表为空，请在 TASK_CONFIGS 中添加任务配置")
    else:
        total_tasks = len(TASK_CONFIGS)
        print(f"🚀 共有 {total_tasks} 个任务待执行")
        print("=" * 70)
        
        for idx, task_config in enumerate(TASK_CONFIGS, 1):
            print(f"\n{'#' * 70}")
            print(f"# 任务 {idx}/{total_tasks}: {task_config.get('name', '未命名')}")
            print(f"{'#' * 70}\n")
            
            if task_config.get('rollback_mode', False):
                # 回滚模式
                rollback_file = task_config.get('rollback_mapping_file', '')
                if not rollback_file:
                    print(f"❌ 任务 [{task_config.get('name')}] 的回滚映射文件未指定")
                else:
                    rollback_from_mapping(rollback_file, task_config)
            else:
                # 重命名模式
                main(task_config)
            
            print("\n")
        
        print("=" * 70)
        print(f"🎊 全部 {total_tasks} 个任务执行完毕!")
        print("=" * 70)
