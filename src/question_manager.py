# question_manager.py
# -*- coding: utf-8 -*-

import questions_data


def read_questions(docx_path=None):
    """直接返回 questions_data 中预定义的题目列表。"""
    return questions_data.QUESTIONS


def read_music_list(docx_path=None):
    """直接返回预定义的音乐信息列表。"""
    # 定义 8 首音乐的 ID 和象限（1~4象限分别对应ID 1-2, 3-4, 5-6, 7-8）
    tracks = []
    quadrant = 0
    for mid in range(1, 9):
        if (mid - 1) % 2 == 0:
            quadrant += 1  # increment quadrant after every two tracks
        tracks.append({
            "id": mid,
            "name": f"Music_{mid}",  # 名称可根据需要修改
            "quadrant": quadrant
        })
    # 不包含空白音乐（ID 0）在列表中
    return tracks
