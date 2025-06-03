def extract_sequence(text):
    """
    从EDF标注信息文本中提取11和12的序列
    Args:
        text: 包含EDF标注信息的文本
    Returns:
        list: 包含11和12的序列列表
    """
    sequence = []
    # 找到标注详情部分的开始
    lines = text.split('\n')
    start_processing = False
    
    for line in lines:
        # 跳过空行
        if not line.strip():
            continue
            
        # 检查是否到达标注详情部分
        if '标注详情' in line:
            start_processing = True
            continue
            
        # 检查是否到达统计部分
        if '标注统计' in line:
            break
            
        # 如果已经到达标注详情部分，开始处理
        if start_processing:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                try:
                    label = float(parts[2].replace('s', ''))  # 移除's'并转换为float
                    if label in [11.0, 12.0]:
                        sequence.append(int(label))
                except ValueError:
                    continue
    
    return sequence

def main():
    filename = './edf_output/train_2_annotations.txt'
    
    # 从EDF输出文件读取数据
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # 检查文件内容是否包含预期的标记
        if '标注详情' not in text:
            print(f"错误：文件 '{filename}' 不是有效的EDF标注信息文件")
            print("提示：请确保文件包含EDF标注信息，而不是EEG数据")
            print("文件开头内容预览：")
            print("---")
            print(text[:200] + "...")
            print("---")
            return
            
    except FileNotFoundError:
        print(f"错误：找不到文件 '{filename}'")
        return
    except Exception as e:
        print(f"错误：读取文件时出错 - {str(e)}")
        return
    
    # 提取序列
    sequence = extract_sequence(text)
    
    # 打印结果
    print("提取的11和12序列:")
    print(sequence)
    print("\n序列表示(用于复制):")
    print(f"custom_sequence = {sequence}")
    
    # 打印序列长度
    print(f"\n序列长度: {len(sequence)}")
    
    # 统计11和12的数量
    count_11 = sequence.count(11)
    count_12 = sequence.count(12)
    print(f"\n11的数量: {count_11}")
    print(f"12的数量: {count_12}")
    
    # 验证总数
    print(f"\n序列完整性验证:")
    print(f"提取的总数 (11 + 12): {count_11 + count_12}")
    print(f"预期的总数: {101}  (根据原文件统计信息)")  # 55 + 46 = 101

if __name__ == "__main__":
    main()