import mne
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.animation import FuncAnimation
import json

rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class EdfVisualizer:
    def __init__(self, edf_path, window_size=1000, json_window_size=10):
        # 读取EDF文件
        self.raw = mne.io.read_raw_edf(edf_path, preload=True)
        
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
        
        # 打印基本信息
        print("\n=== EDF文件信息 ===")
        print(f"采样频率: {self.raw.info['sfreq']} Hz")
        print(f"通道数: {len(self.raw.ch_names)}")
        print(f"通道名称: {self.raw.ch_names}")
        print(f"记录时长: {self.times.max():.2f} 秒")

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

    def get_json_data(self):
        """生成JSON格式的数据"""
        # 获取当前窗口的数据
        end_pos = self.json_current_pos + self.json_window_size
        if end_pos >= len(self.times):
            self.json_current_pos = 0
            end_pos = self.json_window_size
        
        # 获取所有通道的数据窗口
        data_window = self.data[:, self.json_current_pos:end_pos]
        
        # 将数据转换为正确的格式
        # 因为原始数据单位是μV，我们需要将其映射到合适的范围
        # 这里我们假设数据需要映射到0-65535的范围
        # 首先将数据标准化到-1到1之间
        data_min = np.min(self.data)
        data_max = np.max(self.data)
        normalized_data = ((data_window - data_min) / (data_max - data_min) * 65535).astype(int)
        
        # 创建JSON数据
        json_data = {
            "mac": "d5:5:82:f0:1e:a",  # 示例MAC地址
            "chn": str(len(self.raw.ch_names)),
            "pkn": self.packet_counter,
            "eeg": normalized_data.flatten().tolist(),
            "acc": [0, 0, 0, 0]  # 示例加速度数据
        }
        
        self.json_current_pos += self.json_window_size
        self.packet_counter += 1
        
        return json.dumps(json_data)

def create_visualizer(edf_file):
    """创建并返回一个EdfVisualizer实例"""
    try:
        visualizer = EdfVisualizer(edf_file)
        visualizer.print_stats()
        return visualizer
    except Exception as e:
        print(f"错误: 无法创建可视化器: {str(e)}")
        return None

if __name__ == "__main__":
    # 指定EDF文件路径
    edf_file = "./training_data/mi_train_01.edf"  # 请替换为实际的EDF文件路径
    
    try:
        # 创建可视化器
        visualizer = create_visualizer(edf_file)
        if visualizer:
            print("\n开始数据可视化...")
            visualizer.animate()
            plt.show()
    except KeyboardInterrupt:
        print("\n用户终止了程序")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")