import os
import re
import random
import json
from datetime import datetime

# ==================== 配置区域 ====================

# 🔴 重要控制变量
ONLY_MODIFY_PREFIX = False  # True: 只替换前缀，保留原有中间部分和后缀
                            # False: 完全重命名（修改前缀、中间部分、后缀）
# 是否执行回滚操作
ROLLBACK_MODE = False  # True: 回滚模式，False: 重命名模式

# 🆕 回滚配置 - 当 ROLLBACK_MODE = True 时需要指定映射文件路径
ROLLBACK_MAPPING_FILE = '/Users/qc/Desktop/未命名文件夹/QGlasses_20260123_180735.json'

# 是否只处理目标文件夹当前层（不包含子目录）
only_current_level = False

# 路径配置
# 需要修改的特定文件夹
target_folder = '/Users/qc/Desktop/AppStore/NDSTPP/NDSTPP/OldClasses/Section/Detail/Mine'

# 前缀配置
old_prefixes = ['QG', 'QC', 'QIF','NST','NP']  # 可匹配的旧前缀
new_prefixes = ['NDM', 'NM']  # 新的前缀数组，可随机选择


# 项目根路径
project_path = '/Users/qc/Desktop/AppStore/NDSTPP/NDSTPP'
pbxpro_path = '/Users/qc/Desktop/AppStore/NDSTPP/NDSTPP.xcodeproj/project.pbxproj'

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
    }
]


# 中间词库（三组单词）
middle_word_groups = [
    # 第一组
    [
        'Home', 'Account', 'Profile', 'Member', 'User', 'Access', 'Login', 'Bind', 'Authorize', 'Permission',
        'Device', 'Devices', 'Connect', 'Pair', 'Manage', 'Control', 'Monitor', 'Status', 'Overview', 'Dashboard',
        'Usage', 'History', 'Record', 'Report', 'Summary', 'Insight', 'Activity', 'Task', 'Progress', 'Notification',
        'Message', 'Alert', 'Reminder', 'Support', 'Help', 'Guide', 'Tutorial', 'Update', 'Version', 'About',
        'Power', 'Battery', 'Runtime', 'Health', 'Setting', 'Preference', 'Option', 'Config'
    ],
    # 第二组
    [
        'Center', 'Console', 'Panel', 'Workspace', 'Entry', 'Shortcut', 'Quick', 'Sync', 'Share', 'Transfer',
        'Group', 'Scene', 'Mode', 'Preset', 'Routine', 'Automation', 'Schedule', 'Timer', 'Trigger', 'Rule',
        'Bind', 'Unbind', 'Reconnect', 'Switch', 'Add', 'Remove', 'Select', 'Manage', 'Control', 'Adjust',
        'Notify', 'Alert', 'Message', 'Inbox', 'Activity', 'Log', 'Statistic', 'Progress', 'Status', 'Detail',
        'Setting', 'Preference', 'Option', 'Customize', 'Config', 'Save', 'Reset', 'Apply'
    ],
    # 第三组
    [
        'Service', 'Feature', 'Capability', 'Experience', 'Assistant', 'Insight', 'Recommendation', 'Guide', 'Setup', 'Activation',
        'Subscription', 'Plan', 'Package', 'Upgrade', 'Renew', 'Trial', 'Benefit', 'Privilege', 'Usage', 'Quota',
        'Limit', 'Billing', 'Order', 'Invoice', 'Receipt', 'History', 'Record', 'Consumption', 'Security', 'Privacy',
        'Backup', 'Restore', 'Sync', 'Cloud', 'Support', 'Feedback', 'Survey', 'Rating', 'Review', 'About',
        'Center', 'Help', 'Service', 'Data', 'Account', 'Profile'
    ]
]

# 支持的文件类型
suf_set = ('.h', '.m', '.swift')

# ==================== JSON映射文件管理 ====================

def get_mapping_file_path():
    """根据项目路径生成映射文件名"""
    project_name = os.path.basename(project_path.rstrip('/'))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    mapping_filename = f"{project_name}_{timestamp}.json"
    return os.path.join(os.path.dirname(__file__), mapping_filename)

def save_mapping_to_json(mapping_dict, mapping_file):
    """保存映射关系到JSON文件"""
    mapping_data = {
        'timestamp': datetime.now().isoformat(),
        'project_path': project_path,
        'target_folder': target_folder,
        'pbxproj_path': pbxpro_path,
        'only_modify_prefix': ONLY_MODIFY_PREFIX,
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

def rollback_from_mapping(mapping_file):
    """根据映射文件回滚重命名操作"""
    print(f"🔄 开始回滚操作...")
    print(f"📂 映射文件: {mapping_file}")
    
    mapping_data = load_mapping_from_json(mapping_file)
    if not mapping_data:
        return
    
    # 使用映射文件中保存的路径
    saved_project_path = mapping_data.get('project_path', project_path)
    saved_pbxproj_path = mapping_data.get('pbxproj_path', pbxpro_path)
    
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

def parse_class_name(class_name, suffix_config):
    """解析类名为前缀、中间、后缀三部分"""
    matched_prefix = None
    for prefix in old_prefixes:
        if class_name.startswith(prefix):
            matched_prefix = prefix
            break
    
    if not matched_prefix:
        return None, None, None
    
    if ONLY_MODIFY_PREFIX:
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

def generate_new_class_name(old_class_name, suffix_config, used_names, used_full_names, existing_classes=None):
    """
    生成新的类名，支持去重
    Args:
        old_class_name: 原类名
        suffix_config: 后缀配置
        used_names: 已使用的中间名集合
        used_full_names: 已使用的完整类名集合
        existing_classes: 项目中现有的类名集合（用于冲突检测）
    """
    if existing_classes is None:
        existing_classes = set()
    
    old_prefix, middle_part, old_suffix = parse_class_name(old_class_name, suffix_config)
    
    if old_prefix is None:
        return None
    
    if ONLY_MODIFY_PREFIX:
        max_attempts = 50
        for attempt in range(max_attempts):
            new_prefix = random.choice(new_prefixes)
            new_class_name = new_prefix + middle_part
            
            # 🔥 检查是否与现有类名冲突 + 本次生成的类名冲突
            if new_class_name not in existing_classes and new_class_name not in used_full_names:
                used_full_names.add(new_class_name)
                return new_class_name
        
        # 兜底：使用数字后缀
        new_prefix = random.choice(new_prefixes)
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
    
    # 🔥 支持完整类名去重（包括现有类名检测）
    max_attempts = 50
    for attempt in range(max_attempts):
        new_middle = generate_middle_name(used_names)
        new_prefix = random.choice(new_prefixes)
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

def is_in_target_folder(file_path):
    """检查文件是否在目标文件夹中"""
    abs_target = os.path.abspath(target_folder)
    abs_file = os.path.abspath(file_path)
    if only_current_level:
        return os.path.dirname(abs_file) == abs_target
    try:
        common = os.path.commonpath([abs_target, abs_file])
        return common == abs_target
    except Exception:
        return False

def validate_config():
    """验证配置的有效性"""
    print("🔍 验证配置...")
    
    if not os.path.exists(project_path):
        print(f"❌ 项目路径不存在: {project_path}")
        return False
    
    if not os.path.exists(target_folder):
        print(f"❌ 目标文件夹不存在: {target_folder}")
        return False
    
    if not new_prefixes:
        print("❌ 新前缀数组为空")
        return False
    
    if not ONLY_MODIFY_PREFIX:
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

def main():
    print("🚀 工具启动（增强版 v1.4）")
    print(f"⚙️ 运行模式: {'仅修改前缀' if ONLY_MODIFY_PREFIX else '完全重命名'}")
    print(f"📂 项目路径: {project_path}")
    print(f"🎯 目标文件夹: {target_folder}")
    print(f"🔄 前缀: {old_prefixes} -> {new_prefixes}")
    
    if not ONLY_MODIFY_PREFIX:
        print(f"📋 后缀配置组数: {len(suffix_groups)}")
        for group in suffix_groups:
            print(f"  - {group['name']}: {group['old_suffixes']} -> {group['new_suffixes']}")
    
    print("-" * 70)
    
    if not validate_config():
        return
    
    # 🆕 合并所有后缀配置
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
    
    # 🔥 收集项目中现有的类名（排除目标文件夹）
    existing_classes = collect_existing_class_names(project_path, target_folder)
    
    print("📋 扫描需要重命名的文件...")
    renamed_count = 0
    
    for (root, dirs, files) in os.walk(project_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            if not is_in_target_folder(file_path):
                continue
                
            if file_name.endswith(suf_set):
                old_class_name = os.path.splitext(file_name)[0]
                
                # 🆕 尝试匹配所有后缀组
                matched_group = None
                for group in suffix_groups:
                    parsed = parse_class_name(old_class_name, group)
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
                            existing_classes  # 🔥 传入现有类名集合
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
        return
    
    print(f"\n📊 共重命名 {renamed_count} 个文件")
    
    # 🆕 保存映射文件
    mapping_file = get_mapping_file_path()
    save_mapping_to_json(needModifyDic, mapping_file)
    
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
        if os.path.exists(pbxpro_path):
            with open(pbxpro_path, 'r', encoding='utf-8') as f:
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
                with open(pbxpro_path, 'w', encoding='utf-8') as f:
                    f.write(pbx_content)
                print("✅ project.pbxproj 更新完成")
                
    except Exception as e:
        print(f"❌ project.pbxproj 更新失败: {e}")
    
    print("\n" + "="*70)
    print("🎉 任务完成!")
    print(f"📊 重命名文件: {renamed_count}")
    print(f"📊 更新引用: {updated_files_count}")
    print(f"📋 映射文件: {mapping_file}")
    print(f"\n💡 回滚方法:")
    print(f"   1. 将 ROLLBACK_MODE 设置为 True")
    print(f"   2. 将 ROLLBACK_MAPPING_FILE 设置为: {mapping_file}")
    print(f"   3. 重新运行脚本")
    print("="*70)

if __name__ == "__main__":
    if ROLLBACK_MODE:
        # 回滚模式
        if not ROLLBACK_MAPPING_FILE or ROLLBACK_MAPPING_FILE == '/path/to/DPVR_mapping_20260123_143025.json':
            print("❌ 请在配置区域设置正确的 ROLLBACK_MAPPING_FILE 路径")
        else:
            rollback_from_mapping(ROLLBACK_MAPPING_FILE)
    else:
        # 重命名模式
        main()
