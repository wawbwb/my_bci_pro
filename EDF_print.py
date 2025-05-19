import mne
import numpy as np
import pandas as pd

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
    DEFAULT_EDF_FILE = "./training_data/mi_train_01.edf"
    print_edf_content(DEFAULT_EDF_FILE)