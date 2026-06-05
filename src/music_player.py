import pygame
import sys, os

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

def res_path(rel_path: str) -> str:
    """兼容 PyInstaller --onefile 的资源定位"""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS  # PyInstaller 临时解包目录
    elif getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = SOURCE_DIR
    return os.path.join(base, rel_path)

# 配置音乐文件存放路径
# MUSIC_FOLDER = "./music_files/"
MUSIC_FOLDER = res_path("music_files") + os.sep

# 初始化标记（确保 pygame 只初始化一次）
_initialized = False

# 题目选项配图资源（根据题目ID映射选项字母到图片路径）
# OPTION_IMAGES = {
#     3: {  # Q3 油画问题选项对应图片
#         "A": "images/painting_A.jpg",
#         "B": "images/painting_B.jpg"
#     },
#     9: {  # Q9 古董价值问题选项对应图片
#         "A": "images/antique_A.jpg",
#         "B": "images/antique_B.jpg",
#         "C": "images/antique_C.jpg",
#         "D": "images/antique_D.jpg"
#     }
# }

# 2) 题目图片映射
OPTION_IMAGES = {
    3: {
        "A": res_path("images/painting_A.jpg"),
        "B": res_path("images/painting_B.jpg"),
    },
    9: {
        "A": res_path("images/antique_A.jpg"),
        "B": res_path("images/antique_B.jpg"),
        "C": res_path("images/antique_C.jpg"),
        "D": res_path("images/antique_D.jpg"),
    }
}

def init_player():
    """初始化 pygame 混音器，用于播放音频。"""
    global _initialized
    if _initialized:
        return
    try:
        pygame.mixer.init()
        _initialized = True
    except Exception as e:
        print("音频初始化失败:", e)

def play_music(file_path, loop=True):
    """播放背景音乐。如果 loop=True 则循环播放。"""
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(loops=-1 if loop else 0)
    except Exception as e:
        print(f"播放音乐失败: {e}")

def fadeout_music(ms):
    """音乐淡出并停止，ms 为淡出持续的毫秒数。"""
    try:
        pygame.mixer.music.fadeout(ms)
    except Exception as e:
        print(f"音乐淡出失败: {e}")

def stop_music():
    """立即停止音乐播放。"""
    pygame.mixer.music.stop()

def get_file_path(music_id):
    """根据音乐 ID 返回对应的文件路径。ID 0 表示无音乐（静音）。"""
    if music_id == 0:
        return None
    filename = f"music_{music_id}.mp3"  # 例如 music_1.mp3, music_2.mp3, ...
    return MUSIC_FOLDER + filename

def play_test_sound():
    """播放测试音频（用于音量调节提示）。"""
    try:
        # 确保混音器已初始化
        init_player()
        # pygame.mixer.music.load("./music_files/test_sound.mp3")
        pygame.mixer.music.load(res_path("music_files/test_sound.mp3"))
        pygame.mixer.music.play()
    except Exception as e:
        print(f"测试音频播放失败: {e}")
