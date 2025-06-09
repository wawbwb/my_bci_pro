from psychopy.visual import Window
from psychopy.core import Clock, quit
from psychopy.visual import TextStim
# from psychopy.visual import ImageStim
from psychopy.visual import Circle
from psychopy.visual import ShapeStim
from psychopy import event
import random
from psychopy.visual import Rect

import pylsl
from lslReceiver import MarkerInlet
import json

trial_num = 30
image_duration = 4
wanted_inlets = ['curctrl_marker_1']
rest_duration = 3
trial_time = 20
cursor_step = 7

with open('task_markers.json', 'r') as file:
    markers = json.load(file)


def m_wait(t):
    cl = Clock()
    while cl.getTime() < t:
        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            quit()


def check_marker_inlet():
    for inl in inlets:
        print(inl.name)
        if inl.name[:14] == 'curctrl_marker':
            return 's'
    return 'f'


# def run_task():
#     global win,lslRcv,inlets
# ##############


#     id_num = random.randint(1, 10000)
#     name_str = 'psycho_marker_'+str(id_num)
#     info = pylsl.stream_info(name = name_str, type='Markers', channel_count=1,
#                       channel_format='int32', source_id='psycho_marker_005')
#     outlet = pylsl.stream_outlet(info)  

#     inlets=[]
#     streams = pylsl.resolve_streams()
#     for info in streams:
#         if wanted_inlets is not None: # if not none, then only search for this specific inlet; if is none, then search all
#             if info.source_id() in wanted_inlets:
#                 print('Adding inlet: ' + info.name())
#                 if info.type() == 'Markers':
#                     inlets.append(MarkerInlet(info,'Markers'))

#     if (check_marker_inlet()=='s'):
#         print('suc')
#     else:
#         print('failed, quit')
#         # win.close()

#         ####################################################################################
#         quit()

#     print('continue...')

# # ############################
#     win_size=(480, 360)

#     win = Window(size=win_size, fullscr=False)

#     # Initialize a (global) clock
#     # clock = Clock()

#     # # Initialize Keyboard
#     # kb = Keyboard()

#     ### START BODY OF EXPERIMENT ###

#     # instruction_stim = ImageStim(win, 'images/instruction_mi_train.PNG')
#     # left_arrow = ImageStim(win, 'images/left_arrow.PNG')
#     # right_arrow = ImageStim(win, 'images/right_arrow.PNG')

#     # instruction_stim.draw()

#     instruction_text = TextStim(win,'''Imagine movements or relax as in the training session...
#                                                 for example:
# Imagine lifting weight to make ball goes up, and relax to make the ball goes down

# Press any key to begin''')
#     instruction_text.draw()

#     win.flip()

#     # outlet.push_sample(markers['test'])

#     event.waitKeys()

#     outlet.push_sample(markers['task_cursor_control'])

#     outlet.push_sample(markers['begin'])

#     stim_circle = Circle(win,radius=10,edges=128,units='pix',pos=(0,0),
#         fillColor=[1,0.5,0.5625])
#     stim_circle.draw()

#     left_right_rect_width = 20
#     rect_pos_horizontal = int((win_size[0]-left_right_rect_width)/2)
#     # print(rect_pos_horizontal)

#     face_color_not_active = [0.4375,0.5,0.5625]
#     face_color_active = [1,0.5,0.5625]


#     left_rect = Rect(win,width=left_right_rect_width,height=50,units='pix',pos=(-rect_pos_horizontal, 0), 
#         fillColor=face_color_not_active)

#     right_rect = Rect(win,width=left_right_rect_width,height=50,units='pix',pos=(rect_pos_horizontal, 0), 
#         fillColor=face_color_not_active)

#     # left_rect.draw()
#     # right_rect.draw()

#     top_bottom_rect_height = 20
#     rect_pos_vertical = int((win_size[1]-top_bottom_rect_height)/2)
#     # print(rect_pos_vertical)

#     top_rect = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,-rect_pos_vertical), 
#         fillColor=face_color_not_active)

#     bottom_rect = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,rect_pos_vertical), 
#         fillColor=face_color_not_active)

#     top_bottom_rect_thr = int(win_size[1]/2-top_bottom_rect_height)

#     target_rec = Rect(win,width=50,height=top_bottom_rect_height,units='pix',pos=(0,-rect_pos_vertical), 
#         fillColor=face_color_not_active)

#     # top_rect.draw()
#     # bottom_rect.draw()

#     center_text = TextStim(win,'0')
#     center_text.size=0.3
#     default_color = center_text.color

#     def draw_all():
#         # right_rect.draw()
#         # left_rect.draw()
#         top_rect.draw()
#         bottom_rect.draw()


#     for i in range(trial_num):

#         print("remain trials: "+str(trial_num - i))
#         # draw_all()

#         rn = random.randint(1, 1000)

#         if not rn % 2:
#             # top_rect.draw()
#             target_rec.pos = (0,-rect_pos_vertical)
#             target_on_top_bottom=-1
#         else:
#             # bottom_rect.draw()
#             target_rec.pos = (0,rect_pos_vertical)
#             target_on_top_bottom=1

#         target_rec.draw()
#         stim_circle.draw()
#         center_text.setText('4')
#         center_text.draw()
#         win.flip()
#         m_wait(1)

#         target_rec.draw()
#         stim_circle.draw()
#         center_text.setText('3')
#         center_text.draw()
#         win.flip()
#         m_wait(1)

#         target_rec.draw()
#         stim_circle.draw()
#         center_text.setText('2')
#         center_text.draw()
#         win.flip()
#         m_wait(1)

#         target_rec.draw()
#         stim_circle.draw()
#         center_text.setText('1')
#         center_text.draw()
#         win.flip()
#         m_wait(1)
        
#         delta_pos = (0,0)


#         if target_on_top_bottom<0:
#             outlet.push_sample(markers['curctrl_target_bottom'])
#         else:
#             outlet.push_sample(markers['curctrl_target_top'])


#         target_rec.draw()

#         stim_circle.draw()
#         win.flip()

#         rr = 0

#         cl = Clock()
#         while cl.getTime() < trial_time:
#             keys = event.getKeys()
#             # if len(keys)>0:
#             #     print(keys)
#             if 'escape' in keys:
#                 win.close()
#                 quit()

#             r = 0
#             delta_pos = (0,0)

#             if (inlets[0].name[:14] == 'curctrl_marker'):
#                 ts,d = inlets[0].pull_data()
#                 if not len(ts)>0:
#                     continue
#             else:
#                 continue

#             if d[0]==markers['mu_rhythm_high']:
#                 delta_pos = (0,-cursor_step*2)
#             elif d[0]==markers['mu_rhythm_low']:
#                 delta_pos = (0,cursor_step)
#             else:
#                 pass

#             stim_circle.pos += delta_pos

#             if int(stim_circle.pos[1])>-top_bottom_rect_thr and int(stim_circle.pos[1])<top_bottom_rect_thr:
#                 pass
#             else:
#                 if target_on_top_bottom>0:
#                     if stim_circle.pos[1]>0:
#                         target_rec.fillColor = face_color_active
#                         rr = 1
#                     else:
#                         target_rec.fillColor = [1,0,0]
#                         stim_circle.fillColor = [1,0,0] #wrong color
#                         rr = 2

#                 else:
#                     if stim_circle.pos[1]<0:
#                         target_rec.fillColor = face_color_active
#                         rr = 1
#                     else:
#                         target_rec.fillColor = [1,0,0]
#                         stim_circle.fillColor = [1,0,0] #wrong color
#                         rr = 2

#                 # print('get edges')
#                 target_rec.draw()
#                 stim_circle.draw()
#                 win.flip()
#                 break

#             target_rec.draw()
#             stim_circle.draw()
#             win.flip()


#         if rr == 0:
#             center_text.setText('time out')
#             outlet.push_sample(markers['time_out'])
#         elif rr == 1:
#             center_text.setText('correct')
#             center_text.color = face_color_active
#             outlet.push_sample(markers['correct'])
#         elif rr==2:
#             center_text.setText('wrong')
#             center_text.color = [1,0,0]
#             outlet.push_sample(markers['wrong'])

#         target_rec.draw()
#         stim_circle.draw()
#         center_text.draw()
#         win.flip()
#         m_wait(0.5) # show the rect light up 

#         stim_circle.pos=(0,0)
#         target_rec.fillColor=face_color_not_active
#         stim_circle.fillColor=[1,0.5,0.5625]
#         center_text.color = default_color 

#         m_wait(rest_duration)


#     win.close()
#     quit()

def run_task(target_sequence=None, control_sequence=None):
    """
    运行光标控制测试任务
    参数:
        target_sequence: 目标位置序列列表, 11表示上方,12表示下方
            如果为None则随机生成30次trial的序列
        control_sequence: 控制信号序列列表, 与markers中的值对应
            如果为None则从LSL接收控制信号
    """
    global win, lslRcv, inlets

    # 如果没有提供目标序列,则随机生成
    if target_sequence is None:
        target_sequence = []
        for _ in range(trial_num):
            rn = random.randint(1, 1000)
            target_sequence.append(11 if rn % 2 else 12)
    
    # 设置trial数量为序列长度
    actual_trial_num = len(target_sequence)

    # 如果提供了控制序列，确保其长度足够
    if control_sequence is not None:
        required_length = actual_trial_num * 80  # 每个trial需要80个控制信号
        if len(control_sequence) < required_length:
            raise ValueError(f"控制序列长度不足，需要{required_length}个信号，但只提供了{len(control_sequence)}个")
    # LSL设置
    id_num = random.randint(1, 10000)
    name_str = 'psycho_marker_'+str(id_num)
    info = pylsl.stream_info(name=name_str, type='Markers', channel_count=1,
                      channel_format='int32', source_id='psycho_marker_005')
    outlet = pylsl.stream_outlet(info)

    # 只在需要LSL输入时初始化
    if control_sequence is None:
        inlets = []
        streams = pylsl.resolve_streams()
        for info in streams:
            if wanted_inlets is not None:
                if info.source_id() in wanted_inlets:
                    print('Adding inlet: ' + info.name())
                    if info.type() == 'Markers':
                        inlets.append(MarkerInlet(info, 'Markers'))

        if check_marker_inlet() == 's':
            print('suc')
        else:
            print('failed, quit')
            quit()

    print('continue...')

    # 创建窗口和视觉组件
    win_size=(480, 360)
    win = Window(size=win_size, fullscr=False)

    # 显示说明文字
    instruction_text = TextStim(win,'''Imagine movements or relax as in the training session...
                                                for example:
Imagine lifting weight to make ball goes up, and relax to make the ball goes down

Press any key to begin''')
    instruction_text.draw()
    win.flip()
    event.waitKeys()

    # 发送开始标记
    outlet.push_sample(markers['task_cursor_control'])
    outlet.push_sample(markers['begin'])

    # 创建视觉组件
    stim_circle = Circle(win,radius=10,edges=128,units='pix',pos=(0,0),
        fillColor=[1,0.5,0.5625])
    
    # 设置颜色和大小参数
    face_color_not_active = [0.4375,0.5,0.5625]
    face_color_active = [1,0.5,0.5625]
    
    # 创建目标矩形
    top_bottom_rect_height = 20
    rect_pos_vertical = int((win_size[1]-top_bottom_rect_height)/2)
    target_rec = Rect(win,width=50,height=top_bottom_rect_height,units='pix',
                     pos=(0,-rect_pos_vertical), fillColor=face_color_not_active)
    
    top_bottom_rect_thr = int(win_size[1]/2-top_bottom_rect_height)
    
    # 创建文本显示
    center_text = TextStim(win,'0')
    center_text.size=0.3
    default_color = center_text.color

    # 主试验循环
    for i in range(actual_trial_num):
        print("remain trials: "+str(actual_trial_num - i))
        
        # 设置目标位置
        target_on_top_bottom = target_sequence[i]
        target_rec.pos = (0, rect_pos_vertical if target_on_top_bottom == 11 else -rect_pos_vertical)

        # 倒计时
        for count in ['4','3','2','1']:
            target_rec.draw()
            stim_circle.draw()
            center_text.setText(count)
            center_text.draw()
            win.flip()
            m_wait(1)
        
        # 发送目标位置标记
        if target_on_top_bottom == 12:  # 向下
            outlet.push_sample(markers['curctrl_target_bottom'])
        else:  # target_on_top_bottom == 11, 向上
            outlet.push_sample(markers['curctrl_target_top'])

        # 光标控制阶段
        target_rec.draw()
        stim_circle.draw()
        win.flip()
        
        rr = 0
        cl = Clock()
        control_idx = i * 80  # 每个trial固定80个控制信号
        last_update_time = -1
        update_interval = trial_time / 80  # 计算每个控制信号的时间间隔
        
        while cl.getTime() < trial_time:
            if 'escape' in event.getKeys():
                win.close()
                quit()

            current_time = cl.getTime()
            
            if control_sequence is not None:
                # 计算当前应该使用第几个控制信号
                current_signal_idx = int(current_time / update_interval)
                if current_signal_idx > last_update_time and current_signal_idx < 80:
                    d = [control_sequence[control_idx + current_signal_idx]]
                    last_update_time = current_signal_idx
                else:
                    continue
            else:
                # 从LSL接收控制信号，保持原有逻辑不变
                if (inlets[0].name[:14] == 'curctrl_marker'):
                    ts, d = inlets[0].pull_data()
                    if not len(ts)>0:
                        continue
                else:
                    continue

            # 更新光标位置
            if d[0]==markers['mu_rhythm_high']:
                delta_pos = (0,-cursor_step*2)
            elif d[0]==markers['mu_rhythm_low']:
                delta_pos = (0,cursor_step)
            else:
                delta_pos = (0,0)

            stim_circle.pos += delta_pos

            # 检查是否到达目标
            if int(stim_circle.pos[1])>-top_bottom_rect_thr and int(stim_circle.pos[1])<top_bottom_rect_thr:
                pass
            else:
                if target_on_top_bottom == 11:  # 目标在上方
                    if stim_circle.pos[1]>0:
                        target_rec.fillColor = face_color_active
                        rr = 1
                    else:
                        target_rec.fillColor = [1,0,0]
                        stim_circle.fillColor = [1,0,0]
                        rr = 2
                else:  # target_on_top_bottom == 12, 目标在下方
                    if stim_circle.pos[1]<0:
                        target_rec.fillColor = face_color_active
                        rr = 1
                    else:
                        target_rec.fillColor = [1,0,0]
                        stim_circle.fillColor = [1,0,0]
                        rr = 2

                target_rec.draw()
                stim_circle.draw()
                win.flip()
                break

            target_rec.draw()
            stim_circle.draw()
            win.flip()

        # 显示结果
        if rr == 0:
            center_text.setText('time out')
            outlet.push_sample(markers['time_out'])
        elif rr == 1:
            center_text.setText('correct')
            center_text.color = face_color_active
            outlet.push_sample(markers['correct'])
        elif rr==2:
            center_text.setText('wrong')
            center_text.color = [1,0,0]
            outlet.push_sample(markers['wrong'])

        target_rec.draw()
        stim_circle.draw()
        center_text.draw()
        win.flip()
        m_wait(0.5)

        # 重置状态
        stim_circle.pos=(0,0)
        target_rec.fillColor=face_color_not_active
        stim_circle.fillColor=[1,0.5,0.5625]
        center_text.color = default_color 

        m_wait(rest_duration)

    win.close()
    quit()

if __name__ == '__main__':
    # 示例：使用自定义目标序列
    custom_sequence = [12, 12, 11, 12, 11, 12, 11, 11, 12, 11, 12, 11, 12, 11, 12, 
                       12, 11, 11, 12, 11, 11, 12, 11, 12, 12, 11, 11, 12, 11, 11]
    
    # 生成控制序列 (每个trial固定80个控制信号)
    control_signals = []
    signals_per_trial = 80  # 每个trial固定80个信号
    
    # 为每个目标生成带有随机性的控制信号
    import random
    for target in custom_sequence:
        trial_signals = []
        if target == 11:  # 目标在上方，需要向上移动
            # 70%的概率是向上的信号，30%的概率是向下的信号
            for _ in range(signals_per_trial):
                if random.random() < 0.9:  # 90%概率
                    trial_signals.append(markers['mu_rhythm_low'])  # 向上信号
                else:
                    trial_signals.append(markers['mu_rhythm_high'])  # 向下信号
        else:  # 目标在下方，需要向下移动
            # 70%的概率是向下的信号，10%的概率是向上的信号
            for _ in range(signals_per_trial):
                if random.random() < 0.9:  # 90%概率
                    trial_signals.append(markers['mu_rhythm_high'])  # 向下信号
                else:
                    trial_signals.append(markers['mu_rhythm_low'])  # 向上信号
        control_signals.extend(trial_signals)
    
    # 运行任务
    run_task(custom_sequence, control_signals)
    
    # 或使用LSL控制信号
    # run_task(custom_sequence)
