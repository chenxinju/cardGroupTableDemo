import os
import re
import random

# ==================== 配置区域 ====================

# 前缀配置
old_prefixes = ['SF', 'QC','QIF','HLS','Device','PBF']  # 可匹配的旧前缀
new_prefixes = ['Sd','SHD','SKI','HK','RL',]  # 新的前缀数组，可随机选择

# 后缀配置
old_suffixes = ['Controller', 'ViewController', 'Ctrl', 'VC']  # 可匹配的旧后缀
new_suffixes = ['VC', 'ViewController','ViewCtrl']  # 新的后缀数组，可随机选择

#old_suffixes = ['ViewModel', 'Manager','Info','VM']
#new_suffixes = ['VM', 'ViewModel']

#old_suffixes = ['View','CellItem','Header','ViewItem']
#new_suffixes = ['View','InfoView']

#old_suffixes = ['Cell']
#new_suffixes = ['Cell']



# 路径配置
# 需要修改的特定文件夹
target_folder = '/Users/qc/Desktop/Widget/SFFitRing/SFFitRing/SFFitRing/Main/FitRing/Classes/TabbarHomeModule/DeviceModule/ViewControll'










# 项目根路径
project_path = '/Users/qc/Desktop/Widget/SFFitRing/SFFitRing/SFFitRing'
pbxpro_path = '/Users/qc/Desktop/Widget/SFFitRing/SFFitRing/SFFitRing.xcodeproj/project.pbxproj'






# 是否只处理目标文件夹当前层（不包含子目录）
only_current_level = True


# 中间词库（三组单词）
middle_word_groups = [
# 第一组  Article Module 相关文章模块（60个单词）
['Book','Article','Chapter','Title','Subtitle','Author','Editor','Publisher',
     'Content','Paragraph','Excerpt','Summary','Introduction','Conclusion','Preface',
     'Body','Page','Section','Footnote','Illustration','Image','Figure','Table','Quote',
     'Reference','Bibliography','Annotation','Index','Glossary','Appendix'],

# 第二组  Frequency Module 新闻推送/更新/趋势相关（单词）
['Read','Highlight','Bookmark','Note','Comment','Share','Like','Rate','Favorite',
     'Follow','Subscribe','Save','Review','Recommend','Discuss','Annotate','Search',
     'Explore','Open','Close','Scroll','Flip','Navigate','Preview','Download','Print',
     'Listen','Watch','Track','Engage'],

# 第三组  Information Module 新闻信息/数据/用户管理相关（单词）
['Library','Collection','Catalog','Shelf','Folder','Tag','Category','Topic','Genre',
     'Metadata','Record','Entry','Field','Attribute','Key','Value','Database','Dashboard',
     'Profile','Setting','Preference','History','Progress','ReadingList','Archive','Queue',
     'Session','Tracker','Report','Statistics']

]

# 支持的文件类型
suf_set = ('.h', '.m', '.swift')

# 清洗中间词，去除非法字符并转为驼峰
def sanitize_identifier_component(raw_word):
    # 按非字母数字切分
    parts = re.split(r'[^A-Za-z0-9]+', raw_word.strip())
    parts = [p for p in parts if p]
    if not parts:
        return 'Name'
    tokens = []
    # 二次按照驼峰/数字边界切分
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

# ==================== 核心功能函数 ====================

def parse_class_name(class_name):
    """解析类名为前缀、中间、后缀三部分"""
    # 查找匹配的前缀
    matched_prefix = None
    for prefix in old_prefixes:
        if class_name.startswith(prefix):
            matched_prefix = prefix
            break
    
    if not matched_prefix:
        return None, None, None
    
    # 查找匹配的后缀
    matched_suffix = None
    remaining_after_prefix = class_name[len(matched_prefix):]
    
    for suffix in old_suffixes:
        if class_name.endswith(suffix):
            matched_suffix = suffix
            break
    
    if not matched_suffix:
        return None, None, None
    
    # 提取中间部分
    middle_part = class_name[len(matched_prefix):-len(matched_suffix)]
    
    return matched_prefix, middle_part, matched_suffix

def generate_middle_name(used_names):
    """从词库中随机生成中间部分，确保不重复，严格遵循驼峰命名法"""
    max_attempts = 100
    
    for attempt in range(max_attempts):
        # 随机选择2-3个词
        word_count = random.randint(2, 3)
        selected_words = []
        
        # 从词库中随机选择指定数量的组
        available_groups = random.sample(middle_word_groups, min(word_count, len(middle_word_groups)))
        
        for group in available_groups:
            word = random.choice(group)
            sanitized_word = sanitize_identifier_component(word)
            selected_words.append(sanitized_word)
        
        # 如果词组数量不够，从剩余组中补充
        if len(selected_words) < word_count:
            all_remaining_words = []
            for group in middle_word_groups:
                for word in group:
                    sanitized = sanitize_identifier_component(word)
                    if sanitized not in selected_words:
                        all_remaining_words.append(sanitized)
            
            # 补充到指定数量
            while len(selected_words) < word_count and all_remaining_words:
                additional_word = random.choice(all_remaining_words)
                selected_words.append(additional_word)
                all_remaining_words.remove(additional_word)
        
        # 随机打乱顺序
        random.shuffle(selected_words)
        
        # 组合成驼峰命名法的中间名
        middle_name = ''.join(selected_words)
        
        # 检查是否重复
        if middle_name not in used_names:
            return middle_name
    
    # 如果100次尝试都重复，使用版本号后缀（V2, V3, V4...）
    base_name = 'Generated'
    version = 2
    while f"{base_name}V{version}" in used_names:
        version += 1
    return f"{base_name}V{version}"

def generate_new_class_name(old_class_name, used_names, used_combinations):
    """生成新的类名，确保前缀+后缀的组合不重复"""
    old_prefix, middle_part, old_suffix = parse_class_name(old_class_name)
    
    if not all([old_prefix, middle_part, old_suffix]):
        return None
    
    # 生成新的中间部分（驼峰命名法）
    new_middle = generate_middle_name(used_names)
    used_names.add(new_middle)
    
    # 每次随机选择前缀和后缀（整体唯一性由中间名保证）
    new_prefix = random.choice(new_prefixes)
    new_suffix = random.choice(new_suffixes)
    
    # 组合新类名：新前缀 + 驼峰中间名 + 新后缀
    new_class_name = new_prefix + new_middle + new_suffix
    return new_class_name

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
        print(f"📄 文件重命名: {root_file} -> {new_filename + filetype}")
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
        # 检查是否还在文件头部分（以//开头的注释或空行）
        if in_header:
            stripped = line.strip()
            if stripped.startswith('//') or stripped == '':
                # 仍在文件头，不替换
                result_lines.append(line)
                continue
            else:
                # 离开文件头，开始替换
                in_header = False
        
        # 在非文件头部分进行替换
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
    
    # 检查路径
    if not os.path.exists(project_path):
        print(f"❌ 项目路径不存在: {project_path}")
        return False
    
    if not os.path.exists(target_folder):
        print(f"❌ 目标文件夹不存在: {target_folder}")
        return False
    
    # 检查前后缀数组
    if not new_prefixes or len(new_prefixes) == 0:
        print("❌ 新前缀数组为空")
        return False
    
    if not new_suffixes or len(new_suffixes) == 0:
        print("❌ 新后缀数组为空")
        return False
    
    # 检查词库
    if not middle_word_groups or len(middle_word_groups) == 0:
        print("❌ 中间词库为空")
        return False
    
    for i, group in enumerate(middle_word_groups):
        if not group:
            print(f"❌ 第{i+1}组词库为空")
            return False
    
    print("✅ 配置验证通过")
    return True

# ==================== 主执行逻辑 ====================

def main():
    print("🚀 工具启动（随机前后缀版本）")
    print(f"📂 项目路径: {project_path}")
    print(f"🎯 目标文件夹: {target_folder}")
    print(f"🔄 前缀: {old_prefixes} -> {new_prefixes} (随机选择)")
    print(f"🔄 后缀: {old_suffixes} -> {new_suffixes} (随机选择)")
    print(f"🎲 中间词生成: 随机选择2-3个词组合（严格驼峰命名法）")
    print(f"📚 词库预览: {[word.capitalize() for group in middle_word_groups for word in group[:2]]}")
    print(f"🔢 重复处理: 使用版本号后缀 V2, V3, V4...")
    print("-" * 70)
    
    # 验证配置
    if not validate_config():
        return
    
    # 存储已使用的中间名称，确保不重复
    used_middle_names = set()
    # 存储已使用的前缀+后缀组合
    used_combinations = set()
    # 存储类名映射
    needModifyDic = {}
    
    # 第一步：扫描并重命名符合条件的文件
    print("📋 扫描需要重命名的文件...")
    renamed_count = 0
    
    for (root, dirs, files) in os.walk(project_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # 只处理目标文件夹中的文件
            if not is_in_target_folder(file_path):
                continue
                
            if file_name.endswith(suf_set):
                old_class_name = os.path.splitext(file_name)[0]
                
                # 检查是否符合重命名规则
                parsed_result = parse_class_name(old_class_name)
                if parsed_result[0]:  # 如果能解析出前缀
                    if old_class_name in needModifyDic:
                        new_class_name = needModifyDic[old_class_name]
                    else:
                        new_class_name = generate_new_class_name(old_class_name, used_middle_names, used_combinations)
                        if new_class_name:
                            needModifyDic[old_class_name] = new_class_name
                    
                    if new_class_name:
                        # 进行文件重命名
                        new_filename = file_rename(file_path, old_class_name, new_class_name)
                        if new_filename:
                            print(f"✅ 类名映射: {old_class_name} -> {new_class_name}")
                            renamed_count += 1
    
    if renamed_count == 0:
        print("ℹ️ 没有找到需要重命名的文件")
        return
    
    print(f"\n📊 共找到 {renamed_count} 个文件需要重命名")
    print("📝 完整类名映射:")
    for old_name, new_name in needModifyDic.items():
        print(f"   {old_name} -> {new_name}")
    
    # 第二步：更新所有文件中的类名引用
    print(f"\n🔄 更新整个项目中的类名引用...")
    updated_files_count = 0
    
    for (root, dirs, files) in os.walk(project_path):
        for file_name in files:
            if file_name.endswith(suf_set):
                file_path = os.path.join(root, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    # 检查是否需要更新
                    content_modified = False
                    current_content = original_content
                    
                    for old_class, new_class in needModifyDic.items():
                        if old_class in current_content:
                            current_content = replace_with_header_protection(current_content, old_class, new_class)
                            print(f"  🔧 {file_name}: {old_class} -> {new_class}")
                            content_modified = True
                    
                    # 如果内容有修改，写回文件
                    if content_modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(current_content)
                        updated_files_count += 1
                            
                except Exception as e:
                    print(f"  ❌ 处理文件失败 {file_name}: {e}")
    
    print(f"📊 共更新了 {updated_files_count} 个文件中的引用")
    
    # 第三步：更新 project.pbxproj 文件
    print(f"\n🔧 更新 project.pbxproj 文件...")
    try:
        if os.path.exists(pbxpro_path):
            with open(pbxpro_path, 'r', encoding='utf-8') as f:
                pbx_content = f.read()
            
            pbx_modified = False
            for old_class, new_class in needModifyDic.items():
                replaced_current = False
                for ext in ('.h', '.m', '.swift'):
                    old_filename = old_class + ext
                    new_filename = new_class + ext
                    if old_filename in pbx_content:
                        pbx_content = pbx_content.replace(old_filename, new_filename)
                        replaced_current = True
                if replaced_current:
                    print(f"  🔧 project.pbxproj: {old_class} -> {new_class}")
                    pbx_modified = True
            
            if pbx_modified:
                with open(pbxpro_path, 'w', encoding='utf-8') as f:
                    f.write(pbx_content)
                print("✅ project.pbxproj 更新完成")
            else:
                print("ℹ️ project.pbxproj 无需更新")
        else:
            print(f"⚠️ project.pbxproj 文件不存在: {pbxpro_path}")
            
    except Exception as e:
        print(f"❌ project.pbxproj 更新失败: {e}")
    
    print("\n" + "="*70)
    print("🎉 任务完成!")
    print(f"📊 总计处理: {renamed_count} 个类文件")
    print(f"📊 更新引用: {updated_files_count} 个源文件")
    print(f"🎲 使用了 {len(used_combinations)} 种前缀+后缀组合")
    print("💡 提示: 建议在 Xcode 中清理构建缓存并重新编译项目")
    print("💡 所有生成的类名都严格遵循驼峰命名法规范")
    print("💡 前缀和后缀随机选择，确保多样性")
    print("="*70)

if __name__ == "__main__":
    main()
