from psychopy.visual import Window, TextStim, Circle, Rect
from psychopy import core, event 
from psychopy.core import Clock
from pylsl import StreamInfo, StreamOutlet
import json
import random
import sys
import numpy as np

# 加载marker定义
with open('task_markers.json', 'r') as f:
    MARKERS = json.load(f)

class MITrainingWindow:
    def __init__(self, movement_data=None):
        """
        movement_data: 运动控制序列,形如 [(方向, 持续时间), ...]
                      方向: 1 代表向上运动(目标在上方), -1代表向下运动(目标在下方)
                      持续时间: 秒数
        """
        # 默认参数
        self.trial_num = 30 if movement_data is None else len(movement_data)
        self.movement_data = movement_data or self._generate_default_movements()
        self.rest_duration = 3  # 休息时间
        self.cursor_step = 7   # 小球移动步长
        self.trial_time = 20   # 每个试验的最大时间
          # 创建窗口
        self.win_size = (480, 360)
        self.win = Window(size=self.win_size, fullscr=False)
        
        # 创建视觉组件
        self._create_visual_components()
        
        # 创建LSL输出流
        id_num = random.randint(1, 10000)
        name_str = f'psycho_marker_{id_num}'
        self.info = StreamInfo(name=name_str, type='Markers', 
                             channel_count=1, channel_format='int32',
                             source_id='psycho_marker_005')
        self.outlet = StreamOutlet(self.info)

    def _generate_default_movements(self):
        """生成默认的随机运动序列"""
        movements = []
        for _ in range(self.trial_num):
            direction = 1 if random.randint(0, 1) else -1
            movements.append((direction, self.trial_time))
        return movements

    def _create_visual_components(self):
        """创建所有视觉组件"""        # 运动小球
        self.ball = Circle(
            win=self.win,
            radius=10,
            edges=128,
            units='pix',
            pos=(0, 0),
            fillColor=[1, 0.5, 0.5625]
        )

        # 颜色设置
        self.face_color_not_active = [0.4375, 0.5, 0.5625]
        self.face_color_active = [1, 0.5, 0.5625]        # 矩形参数
        left_right_rect_width = 20
        rect_pos_horizontal = int((self.win_size[0]-left_right_rect_width)/2)
        
        # 左右矩形(保持与原代码一致但不显示)
        self.left_rect = Rect(
            win=self.win,
            width=left_right_rect_width,
            height=50,
            units='pix',
            pos=(-rect_pos_horizontal, 0), 
            fillColor=self.face_color_not_active
        )
        
        self.right_rect = Rect(
            win=self.win,
            width=left_right_rect_width,
            height=50,
            units='pix',
            pos=(rect_pos_horizontal, 0),
            fillColor=self.face_color_not_active
        )

        # 上下矩形
        top_bottom_rect_height = 20
        self.rect_pos_vertical = int((self.win_size[1]-top_bottom_rect_height)/2)
        self.rect_thr = int(self.win_size[1]/2-top_bottom_rect_height)

        # 注意这里top_rect和bottom_rect位置的调换是为了与原代码保持一致
        self.top_rect = Rect(
            win=self.win,
            width=50,
            height=top_bottom_rect_height,
            units='pix',
            pos=(0, -self.rect_pos_vertical),
            fillColor=self.face_color_not_active
        )

        self.bottom_rect = Rect(
            win=self.win,
            width=50,
            height=top_bottom_rect_height,
            units='pix',
            pos=(0, self.rect_pos_vertical),
            fillColor=self.face_color_not_active
        )

        # 目标矩形(用于指示目标位置)
        self.target_rect = Rect(
            win=self.win,
            width=50,
            height=top_bottom_rect_height,
            units='pix',
            pos=(0, -self.rect_pos_vertical),
            fillColor=self.face_color_not_active
        )        # 文本提示
        self.instruction = TextStim(
            win=self.win,
            text='''Imagine movements or relax as in the training session...
                                                for example:
Imagine lifting weight to make ball goes up, and relax to make the ball goes down

Press any key to begin''',
            color='white',
            height=0.07
        )
        
        self.center_text = TextStim(
            win=self.win,
            text='0',
            color='white',
            height=0.3
        )
        self.default_color = self.center_text.color

    def wait(self, duration):
        """等待指定时间,同时检查ESC键"""
        clock = Clock()
        while clock.getTime() < duration:
            keys = event.getKeys()
            if 'escape' in keys:
                self.win.close()
                core.quit()
                sys.exit()
                
    def draw_all(self):
        """绘制所有静态视觉元素"""
        self.top_rect.draw()
        self.bottom_rect.draw()
        # 与原代码一致,不绘制左右矩形:
        # self.left_rect.draw() 
        # self.right_rect.draw()

    def run_trial(self, target_direction, duration):
        """运行单个试验
        target_direction: 1代表目标在上方,-1代表目标在下方
        duration: 试验的最大持续时间
        """
        # 重置状态
        self.ball.pos = (0, 0)
        self.ball.fillColor = self.face_color_active
        self.top_rect.fillColor = self.face_color_not_active
        self.bottom_rect.fillColor = self.face_color_not_active
        self.target_rect.fillColor = self.face_color_not_active
        
        # 设置目标位置
        if target_direction > 0:
            self.target_rect.pos = (0, self.rect_pos_vertical)
            self.send_marker(MARKERS['curctrl_target_top'])
        else:
            self.target_rect.pos = (0, -self.rect_pos_vertical)
            self.send_marker(MARKERS['curctrl_target_bottom'])
        
        # 倒计时
        for i in range(4, 0, -1):
            self.target_rect.draw()
            self.ball.draw()
            self.center_text.setText(str(i))
            self.center_text.draw()
            self.win.flip()
            self.wait(1.0)
        
        # 模拟运动过程
        result = 0  # 0:超时, 1:正确, 2:错误
        clock = Clock()
        
        while clock.getTime() < duration:
            # 根据movement_data决定移动方向
            delta_y = self.cursor_step if target_direction > 0 else -self.cursor_step
            self.ball.pos += (0, delta_y)
            
            # 检查是否到达目标区域
            if abs(int(self.ball.pos[1])) > self.rect_thr:
                if (target_direction > 0 and self.ball.pos[1] > 0) or \
                   (target_direction < 0 and self.ball.pos[1] < 0):
                    self.target_rect.fillColor = self.face_color_active
                    result = 1  # 正确
                else:
                    self.target_rect.fillColor = [1, 0, 0]
                    self.ball.fillColor = [1, 0, 0]  # 错误时变红
                    result = 2  # 错误
                break
            
            # 更新显示
            self.target_rect.draw()
            self.ball.draw() 
            self.win.flip()
            self.wait(0.02)  # 控制移动速度
        
        # 显示结果
        if result == 0:
            self.center_text.setText('time out')
            self.send_marker(MARKERS['time_out'])
        elif result == 1:
            self.center_text.setText('correct')
            self.center_text.color = self.face_color_active
            self.send_marker(MARKERS['correct'])
        else:
            self.center_text.setText('wrong')
            self.center_text.color = [1, 0, 0]
            self.send_marker(MARKERS['wrong'])
        
        self.target_rect.draw()
        self.ball.draw()
        self.center_text.draw()
        self.win.flip()
        self.wait(0.5)  # 显示结果
        
        # 重置状态并休息
        self.ball.pos = (0, 0)
        self.target_rect.fillColor = self.face_color_not_active
        self.ball.fillColor = self.face_color_active
        self.center_text.color = self.default_color
        self.center_text.setText('rest')
        self.center_text.draw()
        self.win.flip()
        self.wait(self.rest_duration)    

    def send_marker(self, marker):
        """发送LSL标记"""
        if isinstance(marker, list):
            # 如果已经是列表,直接发送
            self.outlet.push_sample(marker)
        else:
            # 如果不是列表,转换成列表再发送
            self.outlet.push_sample([marker])

    def run_session(self):
        """运行完整的训练会话"""
        # 显示说明
        self.instruction.draw()
        self.win.flip()
        
        # 等待用户按空格键开始
        event.waitKeys(keyList=['space'])
        
        # 发送开始标记
        self.send_marker(MARKERS['task_cursor_control'])
        self.send_marker(MARKERS['begin'])
        
        # 运行所有试验
        for i, (direction, duration) in enumerate(self.movement_data):
            print(f"剩余试验: {self.trial_num - i}")
            self.run_trial(direction, duration)
            
        # 训练结束
        self.instruction.setText('Training finished\nPress any key to exit')
        self.instruction.draw()
        self.win.flip()
        event.waitKeys()
        
        self.win.close()

if __name__ == '__main__':
    # 创建测试序列
    test_movements = [
        (1, 20),   # 向上运动20秒
        (-1, 20),  # 向下运动20秒
        (1, 20),
        (-1, 20),
        (1, 20)
    ]
    
    # 创建并运行训练窗口
    training = MITrainingWindow(movement_data=test_movements)
    training.run_session()
