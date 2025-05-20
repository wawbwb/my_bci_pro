import mne
import numpy as np
import pandas as pd
from pathlib import Path

def save_edf_to_txt(edf_file, output_dir='./edf_output'):
    """
    将EDF文件的原始内容保存为txt文件
    参数:
        edf_file: EDF文件的路径
        output_dir: 输出目录路径
    """
    try:
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取EDF文件名（不包含扩展名）
        edf_name = Path(edf_file).stem
        
        # 读取EDF文件
        raw = mne.io.read_raw_edf(edf_file, preload=False)
        
        # 保存头文件信息
        header_file = output_path / f"{edf_name}_header.txt"
        raw.info._unlocked = True
        with open(header_file, 'w', encoding='utf-8') as f:
            f.write("=== EDF原始头文件信息 ===\n")
            f.write(str(raw._raw_extras[0]))
        
        # 加载并保存数据记录
        raw.load_data()
        data, times = raw[:, :]
        df = pd.DataFrame(data.T, columns=raw.ch_names)
        df.insert(0, 'Time(s)', times)
        
        # 保存数据到CSV文件（更容易查看的格式）
        data_file = output_path / f"{edf_name}_data.txt"
        df.to_csv(data_file, sep='\t', index=False)
        
        # 保存标注信息
        annotations_file = output_path / f"{edf_name}_annotations.txt"
        annotations = raw.annotations
        with open(annotations_file, 'w', encoding='utf-8') as f:
            f.write("=== EDF标注信息 ===\n")
            f.write(f"总段数: {len(annotations)}\n\n")
            f.write("标注详情 (开始时间, 持续时间, 描述):\n")
            
            # 按时间排序的标注
            sorted_annotations = sorted(zip(annotations.onset, annotations.duration, annotations.description))
            
            # 计算每个标记之间的时间间隔
            for i, (onset, duration, description) in enumerate(sorted_annotations):
                if i < len(sorted_annotations) - 1:
                    next_onset = sorted_annotations[i + 1][0]
                    actual_duration = next_onset - onset
                else:
                    actual_duration = 0  # 最后一个标记
                    
                f.write(f"{onset:.3f}s\t{actual_duration:.3f}s\t{description}\n")
            
            # 添加标注统计信息
            f.write("\n标注统计:\n")
            unique_desc = np.unique(annotations.description, return_counts=True)
            for desc, count in zip(*unique_desc):
                f.write(f"标签 {desc}: {count}个\n")
        
        print(f"\n文件已保存:")
        print(f"头文件信息: {header_file}")
        print(f"数据记录: {data_file}")
        print(f"标注信息: {annotations_file}")
        
        return True
        
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")
        return False

def print_edf_content(edf_file):
    """
    打印EDF文件的原始记录，不做任何处理
    参数:
        edf_file: EDF文件的路径
    """
    try:
        # 读取EDF文件但不预加载，以查看原始格式
        raw = mne.io.read_raw_edf(edf_file, preload=False)
        
        # 打印原始头文件信息
        print("\n=== EDF原始头文件信息 ===")
        raw.info._unlocked = True  # 解锁以访问原始信息
        print(raw._raw_extras[0])  # 显示EDF头文件的原始信息
        
        # 打印所有原始数据记录
        print("\n=== EDF所有原始数据记录 ===")
        raw.load_data()  # 加载数据
        data, times = raw[:, :]
        
        # 使用pandas创建数据框以更好地显示
        df = pd.DataFrame(data.T, columns=raw.ch_names)
        df.insert(0, 'Time(s)', times)  # 添加时间列
        
        # 设置显示选项以显示所有行和列
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        
        print("\n完整数据记录:")
        print(df)
        
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")

if __name__ == "__main__":
    # 设置默认EDF文件路径
    # DEFAULT_EDF_FILE = "./training_data/mi_train_02.edf"
    DEFAULT_EDF_FILE = "./training_data_curctrl/train_3.edf"
    # DEFAULT_EDF_FILE = "./data/05200904/05200904_.edf"
    
    # 打印内容
    # print_edf_content(DEFAULT_EDF_FILE)
    
    # 保存为txt文件
    save_edf_to_txt(DEFAULT_EDF_FILE)

    raw = mne.io.read_raw_edf(DEFAULT_EDF_FILE, preload=True)
    annotations = raw.annotations
    print(annotations)
