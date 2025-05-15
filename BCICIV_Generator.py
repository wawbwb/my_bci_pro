import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.animation import FuncAnimation
import json

rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class SignalReadJsonx:
    DEFAULT_CNT_FILE = 'datasets/BCICIV_1_asc/BCICIV_calib_ds1a_cnt.txt'
    DEFAULT_MRK_FILE = 'datasets/BCICIV_1_asc/BCICIV_calib_ds1a_mrk.txt'
    
    def __init__(self, channels_to_plot=5, window_size=1000, json_window_size=10, cnt_file=None, mrk_file=None):
        # 使用默认文件路径或自定义路径
        cnt_file = cnt_file or self.DEFAULT_CNT_FILE
        mrk_file = mrk_file or self.DEFAULT_MRK_FILE
        
        # 加载数据
        self.cnt_data, self.mrk_data = self.load_data(cnt_file, mrk_file)
        self.channels_to_plot = channels_to_plot
        self.window_size = window_size
          # 获取采样点数和通道数
        self.n_samples, self.n_channels = self.cnt_data.shape
        
        # 选择要显示的通道
        self.selected_channels = np.linspace(0, self.n_channels-1, channels_to_plot, dtype=int)
        
        # 创建图形和子图
        self.fig, self.axes = plt.subplots(channels_to_plot, 1, figsize=(15, 10))
        
        # 初始化时间窗口
        self.current_position = 0
        
        # 为每个试次选择不同颜色
        self.colors = ['b', 'r']
          # 设置y轴范围
        self.y_min = np.min(self.cnt_data)
        self.y_max = np.max(self.cnt_data)

        # SignalReadJsonx相关的属性
        self.json_window_size = json_window_size
        self.json_current_pos = 0
        self.json_data_template = {
            "mac": "d5:5:82:f0:1e:a",
            "chn": str(self.n_channels),
            "pkn": 0,
            "eeg": [],
            "acc": [67, -10, 638, -345]
        }

    @staticmethod
    def load_data(cnt_file, mrk_file):
        # 加载连续EEG信号
        cnt_data = np.loadtxt(cnt_file)
        
        # 加载标记数据
        mrk_data = np.loadtxt(mrk_file)
        
        return cnt_data, mrk_data
        
    def print_data_info(self, json_data=None):
        """
        打印数据集的统计信息
        
        参数:
            json_data: JSON格式的数据字符串(可选)。如果提供，将解析并显示JSON数据的统计信息。
                    如果不提供，将显示原始数据的统计信息。
        """
        if json_data:
            # 解析JSON数据
            data_dict = json.loads(json_data)
            eeg_data = np.array(data_dict['eeg']).reshape(-1, int(data_dict['chn']))
            
            print("\n=== JSON数据统计信息 ===")
            print(f"设备MAC地址: {data_dict['mac']}")
            print(f"通道数: {data_dict['chn']}")
            print(f"数据包序号: {data_dict['pkn']}")
            print(f"采样点数: {len(eeg_data)}")
            
            # 计算基本统计量（需要将数据转换回原始值）
            eeg_data_original = (eeg_data - 32768) / 5
            mean_amplitude = np.mean(eeg_data_original)
            std_amplitude = np.std(eeg_data_original)
            max_amplitude = np.max(eeg_data_original)
            min_amplitude = np.min(eeg_data_original)
            
            print("\n信号统计特征(转换后值):")
            print(f"平均幅值: {mean_amplitude:.2f}")
            print(f"标准差: {std_amplitude:.2f}")
            print(f"最大幅值: {max_amplitude:.2f}")
            print(f"最小幅值: {min_amplitude:.2f}")
            print("=====================")
        else:
            # 原有的数据统计功能
            n_trials = len(self.mrk_data)
            class_1_trials = np.sum(self.mrk_data[:, 1] == 1)
            class_2_trials = np.sum(self.mrk_data[:, 1] == -1)
            
            # 计算信号的基本统计量
            mean_amplitude = np.mean(self.cnt_data)
            std_amplitude = np.std(self.cnt_data)
            max_amplitude = np.max(self.cnt_data)
            min_amplitude = np.min(self.cnt_data)
            
            print("\n=== EEG数据集统计信息 ===")
            print(f"采样点数: {self.n_samples}")
            print(f"通道数: {self.n_channels}")
            print(f"总试次数: {n_trials}")
            print(f"类别1(手运动想象)试次数: {class_1_trials}")
            print(f"类别2(脚运动想象)试次数: {class_2_trials}")
            print("\n信号统计特征:")
            print(f"平均幅值: {mean_amplitude:.2f}")
            print(f"标准差: {std_amplitude:.2f}")
            print(f"最大幅值: {max_amplitude:.2f}")
            print(f"最小幅值: {min_amplitude:.2f}")
            print("=====================")

    def extract_selected_channels(self):
        """
        从原始脑电数据中提取特定通道的数据。
        通道顺序与nfo文件中定义的顺序完全对应。
        
        返回:
        - selected_data: 选中通道的数据，形状为(samples, channels)
        - channel_names: 选中通道的名称列表
        """
        # 定义要提取的通道名称
        target_channels = ['F3', 'F4', 'Fz', 'C3', 'C4', 'Cz', 'P3', 'P4']
        
        # 完整的通道列表（来自nfo文件）
        all_channels = ['AF3', 'AF4', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6', 
                       'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6', 
                       'CFC7', 'CFC5', 'CFC3', 'CFC1', 'CFC2', 'CFC4', 'CFC6', 'CFC8',
                       'T7', 'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'T8',
                       'CCP7', 'CCP5', 'CCP3', 'CCP1', 'CCP2', 'CCP4', 'CCP6', 'CCP8',
                       'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6',
                       'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6',
                       'PO1', 'PO2', 'O1', 'O2']
        
        # 找出目标通道在原始数据中的索引位置
        channel_indices = [all_channels.index(ch) for ch in target_channels]
        
        # 提取选定通道的数据
        selected_data = self.cnt_data[:, channel_indices]
        
        return selected_data, target_channels

    def init_animation(self):
        for ax in self.axes:
            ax.clear()
            ax.grid(True)
        return []
        
    def update(self, frame):
        # 更新当前位置
        self.current_position = frame
        
        # 计算当前窗口的数据范围
        start = max(0, self.current_position)
        end = min(self.n_samples, start + self.window_size)
        
        # 对每个通道进行更新
        for i, ch in enumerate(self.selected_channels):
            self.axes[i].clear()
            self.axes[i].grid(True)
            
            # 绘制EEG信号
            self.axes[i].plot(self.cnt_data[start:end, ch], 'gray', alpha=0.5, label=f'Channel {ch}')
            
            # 在标记点添加垂直线
            for trial in self.mrk_data:
                time_point = int(trial[0])
                class_label = int(trial[1])
                if start <= time_point <= end:  # 只显示当前窗口内的标记
                    relative_pos = time_point - start
                    color = self.colors[0 if class_label == 1 else 1]
                    self.axes[i].axvline(x=relative_pos, color=color, alpha=0.3)
            
            self.axes[i].set_ylabel(f'Ch {ch}')
            self.axes[i].set_ylim([self.y_min, self.y_max])
            
            # 只在最后一个子图上显示x轴标签
            if i == len(self.selected_channels)-1:
                self.axes[i].set_xlabel('Samples')
        
        plt.suptitle('EEG Signals with Trial Markers (Scrolling View)\nBlue: Class 1 (手运动想象), Red: Class -1 (脚运动想象)')
        
        return self.axes 
       
    def plot_eeg_signals(self):
        """
        动态显示EEG信号
        
        参数:
        cnt_data: EEG信号数据, shape为(samples, channels)
        mrk_data: 标记数据, shape为(n_trials, 2)
        channels_to_plot: 要显示的通道数量
        window_size: 滑动窗口大小（采样点数）
        """      
        # 创建动画
        n_frames = self.cnt_data.shape[0] - self.window_size
        ani = FuncAnimation(
            self.fig, 
            self.update,
            init_func=self.init_animation,
            frames=range(0, n_frames, self.window_size//10),  # 每次移动窗口大小的1/10
            interval=100,  # 每100毫秒更新一次
            blit=False,
            repeat=True
        )
        
        plt.tight_layout()
        plt.show()
        
    def get_json_array(self):
        """
        根据当前提取的通道数据生成 JSON 数据。每次调用都会返回下一个窗口的数据。
        
        返回：
        JSON 数据字符串，包含EEG信号数据。
        """
        selected_data, _ = self.extract_selected_channels()
        
        # 如果到达数据末尾，重新开始
        if self.json_current_pos + self.json_window_size >= len(selected_data):
            self.json_current_pos = 0

        # 获取当前窗口的数据
        data_window = selected_data[self.json_current_pos:self.json_current_pos + self.json_window_size]
        
        # 构建 JSON 数据
        json_data = {
            "mac": "d5:5:82:f0:1e:a",
            "chn": str(len(data_window[0])),  # 通道数
            "pkn": self.json_current_pos,
            "eeg": (data_window.flatten() * 5 + 32768).astype(int).tolist(),  # 展平并转换数据
            "acc": [67, -10, 638, -345]
        }
        
        # 更新位置
        self.json_current_pos += self.json_window_size
        
        return json.dumps(json_data)

def main():
    # 创建实例，使用默认数据文件路径
    display = SignalReadJsonx()

    # 打印数据统计信息
    display.print_data_info()  
    
    # 可视化数据
    # display.plot_eeg_signals()
    
    # 获取提取后的JSON数据
    json_data = display.get_json_array()

    # 打印生成的JSON数据统计信息
    display.print_data_info(json_data)

    # 打印JSON数据
    print(json_data)

if __name__ == '__main__':
    main()
