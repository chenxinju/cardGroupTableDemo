import os
import re

# 批量重命名配置 - 支持多个类名对的重命名
rename_pairs = [
                ('QIFStepDataModel', 'WDJStepDataModel'),
                
                ('QIFDeviceManager', 'WDJDeviceManager'),
                
                ('QIThemeManager', 'WDJThemeManager'),
                
                ('QIFAppRefreshHeader', 'WDJAppRefreshHeader'),
                
                
                
             

                
     
                
                ]

# 根据需求搜寻以下文件类型（如项目中使用xib storyboard等情况 可以自行添加）
suf_set = ('.h', '.m', '.swift')
# 项目代码文件根路径
project_path = '/Users/qc/Desktop/AppStore/WDJAPP/WDJAPP/Module'
# 项目project.pbxproj文件路径 需要更新配置文件中的类名
pbxpro_path = '/Users/qc/Desktop/AppStore/WDJAPP/WDJAPP.xcodeproj/project.pbxproj'

# 文件重命名函数，返回新的文件名
def file_rename(file_path, pre_str, pre_to_str):
    root_path = os.path.split(file_path)[0]     # 文件目录
    root_name = os.path.split(file_path)[1]     # 文件名包含扩展名
    filename = os.path.splitext(root_name)[0];  # 文件名
    filetype = os.path.splitext(root_name)[1];  # 文件扩展名

    new_path = os.path.join(root_path, filename.replace(pre_str, pre_to_str) + filetype)    # 拼接新路径
    os.renames(file_path, new_path)             # 文件重命名
    return filename.replace(pre_str, pre_to_str)

# 保护文件头的替换函数
def replace_with_header_protection(file_content, old_str, new_str):
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

# 定义一个字典 key=旧类名 value=新类名
needModifyDic = {}

# 遍历文件，符合规则的进行重命名
for (root, dirs, files) in os.walk(project_path):
    for file_name in files:
        # 检查文件是否匹配任何重命名对
        for pre_str, pre_to_str in rename_pairs:
            if file_name.startswith((pre_str,)) and file_name.endswith(suf_set):
                old_name = os.path.splitext(file_name)[0]
                new_name = file_rename(os.path.join(root, file_name), pre_str, pre_to_str)
                needModifyDic[old_name] = new_name
                break  # 找到匹配就跳出循环

# 遍历文件，在文件中更换新类名的引用
print(needModifyDic)
for (root, dirs, files) in os.walk(project_path):
    for file_name in files:
        if file_name.endswith(suf_set):
            print('-----fileName-------' + file_name)
            with open(os.path.join(root, file_name), 'r+') as f:
                print('========fileName========' + file_name)
                s0 = f.read()
                f.close()
                for key in needModifyDic:
                    if key in s0:
                        with open(os.path.join(root, file_name), 'r+') as f4:
                            original_content = f4.read()
                            # 使用保护文件头的替换函数
                            s1 = replace_with_header_protection(original_content, key, needModifyDic[key])
                            print(key + ' ------> ' + needModifyDic[key])
                            f4.seek(0)
                            f4.write(s1)
                            f4.truncate()
                            f4.close()

# 替换配置文件中的类名
for key in needModifyDic:
    with open(pbxpro_path, 'r+') as f:
        s0 = f.read()
        f.close()
        if key in s0:
            with open(pbxpro_path, 'r+') as f2:
                s = f2.read().replace(key, needModifyDic[key])
                f2.seek(0)
                f2.write(s)
                f2.truncate()
                f2.close()
