import mne
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.animation import FuncAnimation
import json

rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class EdfGeneratorJsonx:
    DEFAULT_EDF_FILE = "./training_data_curctrl/train_2.edf"

    # 类变量，用于保存单例实例
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """获取类的单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_json_data(cls):
        """类方法：直接获取JSON数据，无需手动初始化实例"""
        return cls.get_instance().generate_json_data()
    
    def print_basic_info(self):
        """打印EDF文件的基本信息"""
        print("\n=== EDF文件信息 ===")
        print("初始化EDF可视化器...")
        print(f"EDF文件路径: {self.edf_path}")
        print(f"采样频率: {self.raw.info['sfreq']} Hz")
        print(f"通道数: {len(self.raw.ch_names)}")
        print(f"通道名称: {self.raw.ch_names}")
        print(f"记录时长: {self.times.max():.2f} 秒")    
        
    def __init__(self, edf_path=None, window_size=1000, json_window_size=10):
        # 使用默认文件路径或自定义路径
        self.edf_path = edf_path or self.DEFAULT_EDF_FILE
        
        # 禁止MNE的警告和信息输出
        import warnings
        from contextlib import contextmanager
        import sys, os

        @contextmanager
        def suppress_stdout():
            with open(os.devnull, "w") as devnull:
                old_stdout = sys.stdout
                sys.stdout = devnull
                try:
                    yield
                finally:
                    sys.stdout = old_stdout

        # 在抑制输出的环境中读取EDF文件
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with suppress_stdout():
                # 读取EDF文件
                self.raw = mne.io.read_raw_edf(self.edf_path, preload=True)
                # 只选择EEG通道并设置正确的单位(微伏)
                self.raw.pick_types(eeg=True)
        self.data, self.times = self.raw.get_data(units='uV', return_times=True)
        
        self.window_size = window_size
        self.json_window_size = json_window_size
        
        # 创建图形和子图
        self.fig, self.axes = plt.subplots(8, 1, figsize=(15, 12))
        
        # 设置y轴范围
        self.y_min = np.min(self.data)
        self.y_max = np.max(self.data)
        
        # 初始化位置
        self.current_position = 0
        self.json_current_pos = 0
        self.packet_counter = 0

    def print_stats(self):
        """打印每个通道的统计信息"""
        print("\n=== 通道统计信息 ===")
        for i in range(len(self.raw.ch_names)):
            channel_data = self.data[i]
            stats = {
                '最小值': np.min(channel_data),
                '最大值': np.max(channel_data),
                '均值': np.mean(channel_data),
                '标准差': np.std(channel_data),
                '中位数': np.median(channel_data)
            }
            print(f"\n通道 {self.raw.ch_names[i]}:")
            for key, value in stats.items():
                print(f"{key}: {value:.2f} μV")

    def init_animation(self):
        for ax in self.axes:
            ax.clear()
            ax.grid(True)
        return []

    def update(self, frame):
        """更新动画"""
        # 清除之前的图形
        for ax in self.axes:
            ax.clear()
        
        # 获取当前窗口的数据
        end_pos = self.current_position + self.window_size
        if end_pos >= len(self.times):
            self.current_position = 0
            end_pos = self.window_size
        
        time_window = self.times[self.current_position:end_pos]
        
        # 更新每个通道的数据
        for i, ax in enumerate(self.axes):
            data_window = self.data[i, self.current_position:end_pos]
            ax.plot(time_window, data_window, 'b-', linewidth=0.5)
            
            # 设置轴标签和范围
            ax.set_ylabel(f'{self.raw.ch_names[i]}\n(μV)')
            ax.grid(True)
            ax.set_ylim(self.y_min, self.y_max)
            
            # 只在最后一个子图显示x轴标签
            if i == len(self.axes) - 1:
                ax.set_xlabel('Time (s)')
        
        self.current_position += self.window_size // 10  # 更新位置
        
        return self.axes  
      
    def animate(self):
        """启动动画"""
        # 设置cache_frame_data=False来避免无限缓存
        # 或者可以设置save_count来限制缓存的帧数
        self.ani = FuncAnimation(
            self.fig, 
            self.update, 
            interval=50,
            cache_frame_data=False  # 禁用帧缓存
        )
        plt.tight_layout()
        return self.ani    
      
    def get_json_array(self):
        """生成JSON格式的数据，与BCICIV_Generator保持一致的格式和循环逻辑"""
        # 修改重置逻辑，使用循环方式而不是直接跳回开始
        if self.json_current_pos + self.json_window_size >= len(self.times):
            # 获取剩余数据和需要补充的数据
            remaining_samples = len(self.times) - self.json_current_pos
            data_part1 = self.data[:, self.json_current_pos:]
            data_part2 = self.data[:, :self.json_window_size - remaining_samples]
            data_window = np.concatenate([data_part1, data_part2], axis=1)
            self.json_current_pos = self.json_window_size - remaining_samples
        else:
            data_window = self.data[:, self.json_current_pos:self.json_current_pos + self.json_window_size]
            self.json_current_pos += self.json_window_size

        # 使用直接的数值，不进行复杂的归一化，保持数据的原始特征
        # 由于数据已经在μV单位下，可以直接转换为整数
        # eeg_data = data_window.flatten().astype(int).tolist()
        eeg_data = (data_window.flatten() * 5 + 32768).astype(int).tolist()
        
        # 构建JSON数据，保持与BCICIV_Generator相同的格式
        json_data = {
            "mac": "d5:5:82:f0:1e:a",
            "chn": str(len(self.raw.ch_names)),
            "pkn": self.packet_counter,
            "eeg": eeg_data,
            "acc": [67, -10, 638, -345]  # 使用相同的加速度示例数据
        }
        
        self.packet_counter += 1
        
        return json.dumps(json_data)

if __name__ == "__main__":
    try:
        # 1. 初始化并创建实例
        EDF = EdfGeneratorJsonx()
        
        # 2. 显示基本信息
        EDF.print_basic_info()
        
        # 3. 显示数据统计信息
        EDF.print_stats()
        
        # 4. 显示实时可视化
        print("\n开始数据可视化...")
        EDF.animate()
        plt.show()
        
        # 5. 获取并显示JSON数据
        print("\n获取JSON数据示例:")
        json_data = EDF.get_json_array()
        print(json_data)
        
    except KeyboardInterrupt:
        print("\n用户终止了程序")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")