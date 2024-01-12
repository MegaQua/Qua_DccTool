def smooth_keyframes(object_name, attribute, start_frame, end_frame, cutoff_frequency=0.1, sampling_rate=1):
    """
    对指定对象和属性的关键帧应用平滑滤波器。

    :param object_name: 对象名称
    :param attribute: 属性名称
    :param start_frame: 平滑开始的帧数
    :param end_frame: 平滑结束的帧数
    :param cutoff_frequency: 截止频率，默认为0.1
    :param sampling_rate: 采样率，默认为1
    """
    # 构建MEL命令字符串
    clear_selection_cmd = 'selectKey -clear;'
    select_key_cmd = 'selectKey -add -k -t "{0}:{1}" {2}_{3};'.format(start_frame, end_frame, object_name, attribute)
    filter_curve_cmd = 'filterCurve -f butterworth -cof {0} -sr {1} -kof -sk;'.format(cutoff_frequency, sampling_rate)

    # 执行MEL命令
    mel.eval(clear_selection_cmd)
    mel.eval(select_key_cmd)
    mel.eval(filter_curve_cmd)