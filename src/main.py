# main.py —— 单窗口 Tkinter 实验主程序（统一滚动区域 + 固定字体）
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
from questions_data import QUESTIONS
import time
import uuid
import random
import ctypes
import sys, os

import music_player
import data_logger

os.chdir(os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)))

# ========== DPI 设置（Windows） ==========
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ========== 实验条件准备 ==========
questions = QUESTIONS
participant_id = str(uuid.uuid4())

# 音乐条件：4 个象限各随机一首 + 1 个静音条件
quadrants = [
    [1, 2],  # 高唤醒 + 高价效
    [3, 4],  # 高唤醒 + 低价效
    [5, 6],  # 低唤醒 + 高价效
    [7, 8],  # 低唤醒 + 低价效
]
selected_music = [random.choice(q) for q in quadrants]
selected_music.append(0)  # 0 = 无音乐（空白条件）
random.shuffle(selected_music)

formal_questions = [q for q in questions if q.block == "formal"]
interf_questions = [q for q in questions if q.block == "filler"]
random.shuffle(formal_questions)
random.shuffle(interf_questions)

rounds = []
for i in range(5):
    rq = {
        "round_index": i + 1,
        "music_id": selected_music[i],
        "formal_q": formal_questions[i],
        "interf_q": interf_questions[i],
    }
    if random.random() < 0.5:
        rq["first_q"], rq["second_q"] = rq["formal_q"], rq["interf_q"]
    else:
        rq["first_q"], rq["second_q"] = rq["interf_q"], rq["formal_q"]
    rounds.append(rq)

# ========== 数据结构 ==========
participant_info = {"gender": None, "gender_rt": None, "age_group": None, "age_rt": None}
trial_results = {}  # key: question_id，保存每道题的作答数据
initial_timestamps = {}  # 初次提交时间戳（用于追问延迟计算）
music_ratings = {}  # key: music_id，保存音乐主观评分

# ========== Tk 主窗口 & 字体 ==========
root = tk.Tk()
root.title("实验程序")

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
win_w = int(screen_w * 0.85)
win_h = int(screen_h * 0.85)
x = (screen_w - win_w) // 2
y = (screen_h - win_h) // 2
root.geometry(f"{win_w}x{win_h}+{x}+{y}")
root.resizable(True, True)

root.tk.call("tk", "scaling", 1.0)

FONT_MAIN_SIZE = 44
FONT_BIG_SIZE = 50
FONT_SMALL_SIZE = 40

FONT_MAIN = ("SimSun", FONT_MAIN_SIZE)
FONT_BIG = ("SimSun", FONT_BIG_SIZE)
FONT_SMALL = ("SimSun", FONT_SMALL_SIZE)

root.option_add("*Font", FONT_MAIN)

current_frame = None  # 记录当前 Frame，方便切换和销毁

# 当前正在显示、需要响应滚轮的 Canvas
CURRENT_CANVAS = None
SCROLL_BOUND = False


def show_frame(frame: tk.Frame):
    global current_frame
    if current_frame is not None:
        current_frame.destroy()
    current_frame = frame
    current_frame.pack(fill="both", expand=True)


def create_scrollable_area(parent: tk.Widget):
    """
    创建一个带垂直和水平滚动条的 Canvas + 内容 Frame。
    返回 (canvas, content_frame)。
    """
    global CURRENT_CANVAS, SCROLL_BOUND

    container = tk.Frame(parent)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, highlightthickness=0)
    vbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    hbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)

    canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    vbar.grid(row=0, column=1, sticky="ns")
    hbar.grid(row=1, column=0, sticky="ew")

    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    content = tk.Frame(canvas)
    window_id = canvas.create_window((0, 0), window=content, anchor="nw")

    def on_content_configure(event=None):
        bbox = canvas.bbox("all")
        if bbox is not None:
            canvas.configure(scrollregion=bbox)

    content.bind("<Configure>", on_content_configure)

    def on_canvas_configure(event):
        # 让内部 Frame 的宽度跟随 Canvas 宽度，避免左右留空白
        canvas.itemconfig(window_id, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    # 每创建一个新的滚动区域，就把“当前 canvas”指向它
    CURRENT_CANVAS = canvas

    # 只在第一次调用时绑定全局滚轮事件
    if not SCROLL_BOUND:
        SCROLL_BOUND = True

        def _on_mousewheel(event):
            """全局垂直滚动：鼠标滚轮 / 触控板"""
            if CURRENT_CANVAS is None:
                return
            c = CURRENT_CANVAS
            bbox = c.bbox("all")
            if not bbox:
                return
            x1, y1, x2, y2 = bbox
            content_height = y2 - y1
            view_height = c.winfo_height()
            if content_height <= view_height:
                return

            if getattr(event, "delta", 0) != 0:
                delta = event.delta
                # 兼容 Windows 大滚轮和触控板小步长
                if abs(delta) < 120:
                    step = -1 if delta > 0 else 1
                else:
                    step = int(-delta / 120)
                c.yview_scroll(step, "units")
            else:
                # 某些 Linux 的 Button-4/5
                if getattr(event, "num", None) == 4:
                    c.yview_scroll(-1, "units")
                elif getattr(event, "num", None) == 5:
                    c.yview_scroll(1, "units")

        def _on_mousewheel_horizontal(event):
            """全局水平滚动：Shift + 鼠标滚轮"""
            if CURRENT_CANVAS is None:
                return
            c = CURRENT_CANVAS
            bbox = c.bbox("all")
            if not bbox:
                return
            x1, y1, x2, y2 = bbox
            content_width = x2 - x1
            view_width = c.winfo_width()
            if content_width <= view_width:
                return

            if getattr(event, "delta", 0) != 0:
                delta = event.delta
                if abs(delta) < 120:
                    step = -1 if delta > 0 else 1
                else:
                    step = int(-delta / 120)
                c.xview_scroll(step, "units")

        # 把滚轮统一绑在 root 上，任何控件上滚都作用在当前 Canvas
        root.bind_all("<MouseWheel>", _on_mousewheel)  # Windows / 大部分
        root.bind_all("<Button-4>", _on_mousewheel)  # 某些 Linux
        root.bind_all("<Button-5>", _on_mousewheel)
        root.bind_all("<Shift-MouseWheel>", _on_mousewheel_horizontal)

    return canvas, content


# ========== 实验主流程 ==========
def start_experiment():
    music_player.init_player()

    # root.protocol("WM_DELETE_WINDOW", lambda: None)  # 禁止被试在正式实验中关闭窗口
    def on_close():
        if messagebox.askokcancel("退出实验", "确定要退出实验吗？退出后本次实验的进度将丢失。"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    show_round(0)


def show_round(i: int):
    if i >= len(rounds):
        show_followup_intro()
        return

    round_info = rounds[i]
    music_id = round_info["music_id"]

    if music_id != 0:
        music_file = music_player.get_file_path(music_id)
        music_player.play_music(music_file, loop=True)

    show_question(
        round_info=round_info,
        question=round_info["first_q"],
        position=1,
        round_index=round_info["round_index"],
        callback=lambda: show_second_question(i),
    )


def show_second_question(i: int):
    round_info = rounds[i]
    show_question(
        round_info=round_info,
        question=round_info["second_q"],
        position=2,
        round_index=round_info["round_index"],
        callback=lambda: finish_round(i),
    )


def finish_round(i: int):
    music_player.fadeout_music(2000)

    frame = tk.Frame(root)
    tk.Label(
        frame,
        text=f"第 {rounds[i]['round_index']} 轮结束。\n请休息片刻（约 10 秒）后进入下一轮。",
        font=FONT_BIG,
    ).pack(pady=20)
    btn = tk.Button(
        frame,
        text="继续下一轮",
        font=FONT_MAIN,
        state="disabled",
        command=lambda: show_round(i + 1),
    )
    btn.pack(pady=10)

    root.after(10000, lambda: btn.config(state="normal"))
    show_frame(frame)


# ========== 正式题呈现 ==========
def show_question(round_info, question, position: int, round_index: int, callback):
    """呈现单道题目（题干 + 选项 + 提交），内容放在可滚动区域中。"""
    frame = tk.Frame(root)
    win_w = root.winfo_width() or root.winfo_screenwidth()
    wrap_main = max(win_w - 120, 800)
    wrap_option = max(win_w - 400, 600)

    canvas, content = create_scrollable_area(frame)

    # ---- 题干（包括表格信息）----
    text_str = question.text
    if getattr(question, "table", None):
        text_str += "\n\n选项详情：\n"
        for opt, detail in question.table.items():
            text_str += f"\n{opt} 选项：\n"
            for attr_label, attr_val in detail.items():
                text_str += f"  {attr_label}: {attr_val}\n"

    tk.Label(
        content,
        text=text_str,
        font=FONT_MAIN,
        wraplength=wrap_main,
        justify="left",
        anchor="nw",
    ).pack(fill="x", padx=20, pady=10)

    # ---- 选项列表（含图片选项）----
    selected_var = tk.StringVar(value="")
    mark_labels = {}

    def set_selection(opt_key: str):
        selected_var.set(opt_key)
        for k, lbl in mark_labels.items():
            lbl.config(text="■" if k == opt_key else "□")

    image_paths = getattr(music_player, "OPTION_IMAGES", {}).get(question.id)
    image_refs = []

    if image_paths:
        max_w, max_h = 800, 800
        for opt_key in question.options.keys():
            img_path = image_paths.get(opt_key)

            row = tk.Frame(content)
            row.pack(anchor="w", padx=80, pady=15, fill="x")

            mark = tk.Label(row, text="□", font=FONT_MAIN, width=2)
            mark.pack(side="left", anchor="n", pady=10)
            mark_labels[opt_key] = mark

            right = tk.Frame(row)
            right.pack(side="left", anchor="nw")

            img_label = None
            if img_path:
                try:
                    img = Image.open(img_path)
                    w, h = img.size
                    scale = min(max_w / w, max_h / h)
                    new_size = (int(w * scale), int(h * scale))
                    img = img.resize(new_size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    image_refs.append(photo)
                    img_label = tk.Label(right, image=photo)
                    img_label.pack()
                except Exception as e:
                    print(f"加载图片失败 {img_path}: {e}")

            caption_text = question.options.get(opt_key, "")
            caption = tk.Label(
                right,
                text=f"{opt_key}. {caption_text}",
                font=FONT_SMALL,
                wraplength=wrap_option,
                justify="center",
            )
            caption.pack(pady=(5, 0))

            mark.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))
            caption.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))
            if img_label is not None:
                img_label.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))

        # 将 image_refs 绑定到 content，防止被回收
        content.image_refs = image_refs
    else:
        for opt_key, opt_text in question.options.items():
            display_text = opt_text if opt_text else f"选项 {opt_key}"

            row = tk.Frame(content)
            row.pack(anchor="w", padx=40, pady=6, fill="x")

            mark = tk.Label(row, text="□", font=FONT_MAIN, width=2)
            mark.pack(side="left")
            mark_labels[opt_key] = mark

            text_label = tk.Label(
                row,
                text=f"{opt_key}. {display_text}",
                font=FONT_MAIN,
                anchor="w",
                justify="left",
                wraplength=wrap_option,
            )
            text_label.pack(side="left", fill="x")

            mark.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))
            text_label.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))

    # ---- 提交按钮 ----
    # 记录开始呈现题目的时间戳
    start_ts = time.time()

    def on_submit():
        choice = selected_var.get()
        if not choice:
            return
        qid = question.id
        is_correct = None
        if question.objective and question.correct_option:
            is_correct = 1 if choice == question.correct_option else 0

        trial_results[qid] = {
            "question_id": qid,
            "is_formal": 1 if question.block == "formal" else 0,
            "question_type": 1 if question.objective else 0,
            "round_index": round_index,
            "position_in_round": position,
            "answer_choice": choice,
            "is_correct": is_correct,
            "music_id": round_info["music_id"],
        }
        # 记录初始答题用时（毫秒）
        trial_results[qid]["rt_initial_ms"] = int((time.time() - start_ts) * 1000)
        # 保存初次提交时间用于追问延迟计算
        initial_timestamps[qid] = time.time()
        show_confidence(question, qid, callback)

    submit_btn = tk.Button(content, text="提交", font=FONT_MAIN, command=on_submit)
    submit_btn.pack(pady=15)
    submit_btn.config(state="disabled")

    def on_select_change(*args):
        submit_btn.config(state="normal" if selected_var.get() else "disabled")

    selected_var.trace_add("write", on_select_change)

    # 更新滚动区域范围并显示 Frame
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    show_frame(frame)


def show_confidence(question, qid: int, next_callback):
    """初次作答后的自信度评分。"""
    frame = tk.Frame(root)
    canvas, content = create_scrollable_area(frame)
    # —— 新增：本函数内计算 wrap_main（与 show_question 保持一致）
    win_w = root.winfo_width() or root.winfo_screenwidth()
    wrap_main = max(win_w - 120, 800)
    # 提示说明
    tk.Label(
        content,
        text=(
            "请对刚才答案的自信程度进行评分。\n"
            "自信程度指的是您对自己刚才所选答案有多确定、有多确信它是正确的。\n"
            "无论客观上您的答案是否正确，只要您认为自己答得对，就可以给出较高分数。\n\n"
            "1 = 非常不自信，基本是猜的，完全没有把握\n"
            "2 = 比较不自信，有一点依据，但还是不太确定\n"
            "3 = 中等，一半确定，一半不确定\n"
            "4 = 比较自信，基本确定自己答得对，但还有一点怀疑\n"
            "5 = 非常自信，完全确信自己答得对，没有任何犹豫\n\n"
            "请拖动下方滑块进行评分。"
        ),
        font=FONT_MAIN,
        wraplength=wrap_main,  # 自动换行宽度
        anchor="n",  # 文本锚点在中间
        justify="center"  # 每行文字居中对齐
    ).pack(fill="x", padx=20, pady=(10, 15))

    conf_var = tk.IntVar(value=0)
    scale = tk.Scale(
        content,
        variable=conf_var,
        from_=1,
        to=5,
        orient="horizontal",
        length=400,
        showvalue=True,
        tickinterval=1,
    )
    scale.set(3)
    scale.pack(pady=10)

    start_time = time.time()

    # 不再单独记录滑动条释放时刻，用总时长计算反应时

    def submit_confidence():
        rating = conf_var.get()
        if rating == 0:
            return
        # 保存初始自信评分及反应时
        trial_results[qid]["conf_initial"] = rating
        trial_results[qid]["conf_initial_rt_ms"] = int((time.time() - start_time) * 1000)
        next_callback()

    tk.Button(content, text="确定", font=FONT_MAIN, command=submit_confidence).pack(pady=10)
    # 更新滚动区域范围并显示 Frame
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    show_frame(frame)


# ========== 追问环节 ==========
def show_followup_intro():
    music_player.stop_music()
    frame = tk.Frame(root)
    tk.Label(
        frame,
        text="现在进入追问环节。\n仅针对部分先前回答的问题。",
        font=FONT_BIG,
    ).pack(pady=20)
    tk.Button(frame, text="开始追问", font=FONT_MAIN, command=start_followup).pack(pady=10)
    show_frame(frame)


def start_followup():
    """仅对正式题的主观题，以及正式题（客观题）但回答错误的问题进行追问。"""
    followup_questions = []
    for q in formal_questions:
        res = trial_results.get(q.id)
        if not res:
            continue
        if not q.objective:
            followup_questions.append(q)
        else:
            if res.get("is_correct") == 0:
                followup_questions.append(q)

    random.shuffle(followup_questions)
    for order, fq in enumerate(followup_questions, start=1):
        trial_results[fq.id]["post_shown"] = 1
        trial_results[fq.id]["probe_order"] = order

    if not followup_questions:
        show_music_rating_intro()
        return

    show_followup_question(followup_questions, index=0)


def show_followup_question(followup_list, index: int):
    """追问页1：显示原题 + 提示信息 + 原答案 + 再次自信度评价。"""
    if index >= len(followup_list):
        show_music_rating_intro()
        return

    question = followup_list[index]
    qid = question.id
    res = trial_results[qid]

    frame = tk.Frame(root)
    win_w = root.winfo_width() or root.winfo_screenwidth()
    wrap_main = max(win_w - 120, 800)
    wrap_option = max(win_w - 400, 600)

    canvas, content = create_scrollable_area(frame)

    # 原题题干
    text_str = question.text
    if getattr(question, "table", None):
        text_str += "\n\n选项详情：\n"
        for opt, detail in question.table.items():
            text_str += f"\n{opt} 选项：\n"
            for attr_label, attr_val in detail.items():
                text_str += f"  {attr_label}: {attr_val}\n"

    tk.Label(
        content,
        text=text_str,
        font=FONT_MAIN,
        wraplength=wrap_main,
        justify="left",
        anchor="nw",
    ).pack(fill="x", padx=20, pady=10)

    # 图片回顾（如有）
    image_paths = getattr(music_player, "OPTION_IMAGES", {}).get(question.id)
    image_refs = []
    if image_paths:
        tk.Label(
            content,
            text="图片回顾：",
            font=FONT_BIG,
            anchor="w",
            justify="left",
        ).pack(fill="x", padx=20, pady=(0, 5))

        max_w, max_h = 800, 800
        for opt_key in question.options.keys():
            img_path = image_paths.get(opt_key)

            row = tk.Frame(content)
            row.pack(anchor="w", padx=80, pady=10, fill="x")

            right = tk.Frame(row)
            right.pack(side="left", anchor="nw")

            if img_path:
                try:
                    img = Image.open(img_path)
                    w, h = img.size
                    scale = min(max_w / w, max_h / h)
                    new_size = (int(w * scale), int(h * scale))
                    img = img.resize(new_size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    image_refs.append(photo)
                    img_label = tk.Label(right, image=photo)
                    img_label.pack()
                except Exception as e:
                    print(f"加载图片失败 {img_path}: {e}")

            caption_text = question.options.get(opt_key, "")
            tk.Label(
                right,
                text=f"{opt_key}. {caption_text}",
                font=FONT_SMALL,
                wraplength=wrap_option,
                justify="center",
            ).pack(pady=(5, 0))

        content.image_refs_followup = image_refs

    # 原答案提示
    original_choice = res["answer_choice"]
    original_text = question.options.get(original_choice, "")
    tk.Label(
        content,
        text=f"您之前的回答：{original_choice}. {original_text}",
        font=FONT_MAIN,
        wraplength=wrap_main,
        anchor="w",
        justify="left",
    ).pack(fill="x", padx=20, pady=(10, 15))

    # 负面提示信息（如有）
    info_text = ""
    if question.followups:
        if "general" in question.followups:
            info_text = question.followups["general"]
        else:
            info_text = question.followups.get(original_choice, "")
    if not info_text:
        info_text = "本题没有额外材料，请回顾上述情境后，再次评估您对原答案的自信程度。"

    tk.Label(
        content,
        text="提示信息：",
        font=FONT_MAIN,  # 和题干一致
        anchor="w",
        justify="left",
    ).pack(fill="x", padx=20, pady=(5, 5))
    tk.Label(
        content,
        text=info_text,
        font=FONT_MAIN,  # 和题干一致
        wraplength=wrap_main,
        justify="left",
        anchor="nw",
    ).pack(fill="x", padx=20, pady=(0, 15))

    # 记录追问页面进入延迟（毫秒）
    enter_time = time.time()
    trial_results[qid]["probe_delay_ms"] = int((enter_time - initial_timestamps[qid]) * 1000)

    # 再次自信度评分
    tk.Label(
        content,
        text=(
            "请再次评价您对原答案的自信程度。\n"
            "自信程度指的是您对自己原先选的答案有多确定、有多确信它是正确的。\n"
            "无论客观上您的答案是否正确，只要您认为自己答得对，就可以给出较高分数。\n\n"
            "1 = 非常不自信\n"
            "2 = 比较不自信\n"
            "3 = 中等\n"
            "4 = 比较自信\n"
            "5 = 非常自信\n\n"
            "请拖动下方滑块进行评分。"
        ),
        font=FONT_MAIN,
        wraplength=wrap_main,  # 自动换行宽度
        anchor="n",  # 文本锚点在中间
        justify="center"  # 每行文字居中对齐
    ).pack(fill="x", padx=20, pady=(10, 15))

    conf_var = tk.IntVar(value=0)
    conf_scale = tk.Scale(
        content,
        variable=conf_var,
        from_=1,
        to=5,
        orient="horizontal",
        length=400,
        showvalue=True,
        tickinterval=1,
    )
    conf_scale.set(3)
    conf_scale.pack(pady=5)

    def submit_confidence():
        rating = conf_var.get()
        if rating == 0:
            return
        trial_results[qid]["conf_post_original"] = rating
        trial_results[qid]["conf_post_original_ms"] = int((time.time() - enter_time) * 1000)
        show_followup_reanswer(question, followup_list, index)

    tk.Button(content, text="下一步", font=FONT_MAIN, command=submit_confidence).pack(pady=15)

    # 更新滚动区域范围并显示 Frame
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    show_frame(frame)


def show_followup_reanswer(question, followup_list, index: int):
    """追问页2：再次呈现原题和选项，允许修改或保持原答案。"""
    qid = question.id
    res = trial_results[qid]

    frame = tk.Frame(root)
    win_w = root.winfo_width() or root.winfo_screenwidth()
    wrap_main = max(win_w - 120, 800)
    wrap_option = max(win_w - 400, 600)

    canvas, content = create_scrollable_area(frame)

    # 原题题干
    text_str = question.text
    if getattr(question, "table", None):
        text_str += "\n\n选项详情：\n"
        for opt, detail in question.table.items():
            text_str += f"\n{opt} 选项：\n"
            for attr_label, attr_val in detail.items():
                text_str += f"  {attr_label}: {attr_val}\n"

    tk.Label(
        content,
        text=text_str,
        font=FONT_MAIN,
        wraplength=wrap_main,
        justify="left",
        anchor="nw",
    ).pack(fill="x", padx=20, pady=10)

    # 原答案说明
    original_choice = res["answer_choice"]
    original_text = question.options.get(original_choice, "")
    tk.Label(
        content,
        text=(
            f"您之前的答案是：{original_choice}. {original_text}\n\n"
            "在了解提示信息之后，您可以重新选择一个选项，"
            "也可以保持原来的答案不变。\n"
            "如果希望保持原答案，请再次选择原来的选项后点击“提交”。"
        ),
        font=FONT_MAIN,
        wraplength=wrap_main,
        justify="left",
        anchor="w",
    ).pack(fill="x", padx=20, pady=(5, 15))

    # 选项列表（与初始题相同）
    selected_var = tk.StringVar(value="")
    mark_labels = {}

    image_paths = getattr(music_player, "OPTION_IMAGES", {}).get(question.id)
    image_refs = []

    def set_selection(opt_key: str):
        selected_var.set(opt_key)
        for k, lbl in mark_labels.items():
            lbl.config(text="■" if k == opt_key else "□")

    if image_paths:
        max_w, max_h = 800, 800
        for opt_key in question.options.keys():
            img_path = image_paths.get(opt_key)

            row = tk.Frame(content)
            row.pack(anchor="w", padx=80, pady=15, fill="x")

            mark = tk.Label(row, text="□", font=FONT_MAIN, width=2)
            mark.pack(side="left", anchor="n", pady=10)
            mark_labels[opt_key] = mark

            right = tk.Frame(row)
            right.pack(side="left", anchor="nw")

            img_label = None
            if img_path:
                try:
                    img = Image.open(img_path)
                    w, h = img.size
                    scale = min(max_w / w, max_h / h)
                    new_size = (int(w * scale), int(h * scale))
                    img = img.resize(new_size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    image_refs.append(photo)
                    img_label = tk.Label(right, image=photo)
                    img_label.pack()
                except Exception as e:
                    print(f"加载图片失败 {img_path}: {e}")

            caption_text = question.options.get(opt_key, "")
            caption = tk.Label(
                right,
                text=f"{opt_key}. {caption_text}",
                font=FONT_SMALL,
                wraplength=wrap_option,
                justify="center",
            )
            caption.pack(pady=(5, 0))

            mark.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))
            caption.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))
            if img_label is not None:
                img_label.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))

        content.image_refs_reanswer = image_refs
    else:
        for opt_key, opt_text in question.options.items():
            display_text = opt_text if opt_text else f"选项 {opt_key}"

            row = tk.Frame(content)
            row.pack(anchor="w", padx=40, pady=6, fill="x")

            mark = tk.Label(row, text="□", font=FONT_MAIN, width=2)
            mark.pack(side="left")
            mark_labels[opt_key] = mark

            text_label = tk.Label(
                row,
                text=f"{opt_key}. {display_text}",
                font=FONT_MAIN,
                anchor="w",
                justify="left",
                wraplength=wrap_option,
            )
            text_label.pack(side="left", fill="x")

            mark.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))
            text_label.bind("<Button-1>", lambda e, k=opt_key: set_selection(k))

    submit_btn = tk.Button(content, text="提交", font=FONT_MAIN)
    submit_btn.pack(pady=15)
    submit_btn.config(state="disabled")

    start_time = time.time()

    def on_select_change(*args):
        submit_btn.config(state="normal" if selected_var.get() else "disabled")

    selected_var.trace_add("write", on_select_change)

    def on_submit():
        choice = selected_var.get()
        if not choice:
            return
        original_choice_local = res["answer_choice"]
        res["changed_answer"] = 1 if choice != original_choice_local else 0
        res["changed_answer_ms"] = int((time.time() - start_time) * 1000)
        # 记录最终答案内容
        res["changed_answer_content"] = choice
        show_followup_question(followup_list, index + 1)

    submit_btn.config(command=on_submit)

    # 更新滚动区域范围并显示 Frame
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    show_frame(frame)


# ========== 音乐评分环节 ==========
def show_music_rating_intro():
    frame = tk.Frame(root)
    tk.Label(
        frame,
        text="现在进入音乐评价环节。\n"
             "请按照提示对实验中听到的音乐进行评分。",
        font=FONT_BIG,
    ).pack(pady=20)
    tk.Button(
        frame,
        text="开始音乐评价",
        font=FONT_MAIN,
        command=start_music_ratings,
    ).pack(pady=10)
    show_frame(frame)


def start_music_ratings():
    actual_music_ids = [m for m in selected_music if m != 0]
    random.shuffle(actual_music_ids)
    for order, mid in enumerate(actual_music_ids, start=1):
        music_ratings[mid] = {"rating_order": order}
    show_music_rating_page(actual_music_ids, index=0)


def show_music_rating_page(music_ids, index: int):
    if index >= len(music_ids):
        show_finish_page()
        return

    mid = music_ids[index]
    music_file = music_player.get_file_path(mid)
    music_player.play_music(music_file, loop=False)

    frame = tk.Frame(root)
    canvas, content = create_scrollable_area(frame)
    order = music_ratings[mid]["rating_order"]
    # 计算自动换行宽度
    win_w = root.winfo_width() or root.winfo_screenwidth()
    wrap_main = max(win_w - 120, 800)
    tk.Label(
        content,
        text=f"音乐评价 {order}/{len(music_ids)}",
        font=FONT_BIG,
    ).pack(pady=10)
    tk.Label(
        content,
        text="拖动滑块来评分",
        font=FONT_SMALL,
        fg="gray",
    ).pack(pady=5)

    rating_vars = {
        "arousal": tk.IntVar(value=0),
        "valence": tk.IntVar(value=0),
        "liking": tk.IntVar(value=0),
        "familiarity": tk.IntVar(value=0),
    }
    dimensions = [
        ("唤醒程度\n（指这段音乐带给你在生理和心理上的激活程度，\n"
         "比如紧张、兴奋、精神是否被\"调动起来\"。\n"
         "请只根据你听这段音乐时的感觉来判断，\n"
         "而不是它好不好听\n"
         "1=非常平静, 2=比较平静, 3=中等, 4=比较激动, 5=非常激动）"
             , "arousal"),
        ("积极程度\n（指这段音乐在整体上给你的情绪是愉快还是不愉快。\n"
         "请只根据你听这段音乐时的感觉来判断，\n"
         "而不是它好不好听\n"
         "1=非常不愉快, 2=比较不愉快, 3=中等, 4=比较愉快, 5=非常愉快）"
             , "valence"),
        ("喜爱程度\n（指你主观上对这首音乐的喜欢或不喜欢程度。\n"
         "请根据你直观的喜好打分，\n"
         "而不是从音乐的质量、风格或节奏快慢来判断\n"
         "1=最不喜欢, 2=比较不喜欢, 3=中等, 4=比较喜欢, 5=非常喜欢）"
             , "liking"),
        ("熟悉程度\n（指你对这首音乐的熟悉程度，\n"
         "也就是你是否听过或是否觉得听起来很熟悉\n"
         "你不需要准确说出曲名，只看主观感觉。\n"
         "1=最不熟悉, 2=比较不熟悉, 3=中等, 4=比较熟悉, 5=非常熟悉）"
             , "familiarity"),
    ]
    for text, key in dimensions:
        # 说明文字
        label = tk.Label(
            content,
            text=text,
            font=FONT_SMALL,
            wraplength=wrap_main,  # 自动换行
            justify="center",  # 多行文字居中对齐
            anchor="n"  # 整体居中
        )
        label.pack(fill="x", padx=40, pady=(10, 5))  # 让 Label 随宽度变化

        music_scale = tk.Scale(
            content,
            variable=rating_vars[key],
            from_=1,
            to=5,
            orient="horizontal",
            length=400,
            showvalue=True,
            tickinterval=1,
        )
        music_scale.set(3)
        music_scale.pack(pady=5)

        # 每个 label 单独绑定自己的 resize 回调
        def _on_resize(event, lbl=label):
            lbl.config(wraplength=event.width - 80)

        content.bind("<Configure>", lambda e, lbl=label: _on_resize(e, lbl))

    def submit_ratings():
        vals = {k: v.get() for k, v in rating_vars.items()}
        if any(val == 0 for val in vals.values()):
            return
        music_ratings[mid]["arousal"] = vals["arousal"]
        music_ratings[mid]["valence"] = vals["valence"]
        music_ratings[mid]["liking"] = vals["liking"]
        music_ratings[mid]["familiarity"] = vals["familiarity"]

        music_player.stop_music()
        show_music_rating_page(music_ids, index + 1)

    tk.Button(content, text="提交评分", font=FONT_MAIN, command=submit_ratings).pack(pady=15)
    # 更新滚动区域范围并显示 Frame
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    show_frame(frame)


# ========== 实验结束 & 数据保存 ==========
def show_finish_page():
    data_logger.save_participant_info(participant_id, participant_info, "participants.csv")
    data_logger.save_round_map(participant_id, rounds, "round_map.csv")
    data_logger.save_trials(participant_id, trial_results, "trials.csv")
    data_logger.save_music_ratings(participant_id, music_ratings, rounds, "music_ratings.csv")

    frame = tk.Frame(root)
    tk.Label(frame, text="实验结束！感谢您的参与。", font=FONT_BIG).pack(pady=20)
    tk.Label(
        frame,
        text="结果已保存为四个 CSV 数据表文件:\n"
             "music_ratings.csv,\n"
             "participants.csv,\n"
             "round_map.csv,\n"
             "trials.csv\n"
             "请将这些文件发送给实验负责人。",
        font=FONT_MAIN,
    ).pack(pady=10)
    tk.Button(frame, text="关闭程序", font=FONT_MAIN, command=root.destroy).pack(pady=20)
    show_frame(frame)


# ========== 初始界面：欢迎页 / 基本信息问卷 / 音频测试 / 开始提示 ==========
# 1. 欢迎页
welcome_frame = tk.Frame(root)
tk.Label(welcome_frame, text="欢迎参加本次实验", font=FONT_BIG).pack(pady=30)
welcome_msg = (
    "为方便查找实验结束后自动生成的数据表，\n请确认实验程序位于独立文件夹中。\n\n"
    "实验过程中可能会播放音频，\n请确保在安静环境并佩戴耳机。\n\n"
    "实验全程约 20 分钟，\n请尽量一次性完成，不要中途退出。"
)
tk.Label(
    welcome_frame,
    text=welcome_msg,
    font=FONT_MAIN,
    justify="left",
).pack(padx=20)
tk.Button(
    welcome_frame,
    text="开始实验",
    font=FONT_BIG,
    command=lambda: show_frame(gender_frame),
).pack(pady=20)
tk.Button(welcome_frame, text="退出", font=FONT_MAIN, command=root.destroy).pack(pady=10)
current_frame = welcome_frame
current_frame.pack(fill="both", expand=True)

# 2. 性别信息
gender_frame = tk.Frame(root)
tk.Label(gender_frame, text="请选择您的性别：", font=FONT_BIG).pack(pady=20)
gender_var = tk.StringVar(value="")
gender_mark_labels = {}


def set_gender(code: str):
    gender_var.set(code)
    for c, lbl in gender_mark_labels.items():
        lbl.config(text="■" if c == code else "□")


for label, code in [
    ("男", "male"),
    ("女", "female"),
    ("其他", "other"),
    ("不愿透露", "prefer_not_to_say"),
]:
    row = tk.Frame(gender_frame)
    row.pack(anchor="w", padx=50, pady=6, fill="x")

    mark = tk.Label(row, text="□", font=FONT_MAIN, width=2)
    mark.pack(side="left")

    text_label = tk.Label(row, text=label, font=FONT_MAIN, anchor="w", justify="left")
    text_label.pack(side="left", fill="x")

    gender_mark_labels[code] = mark

    mark.bind("<Button-1>", lambda e, c=code: set_gender(c))
    text_label.bind("<Button-1>", lambda e, c=code: set_gender(c))


def submit_gender():
    if not gender_var.get():
        return
    participant_info["gender"] = gender_var.get()
    participant_info["gender_rt"] = int((time.time() - gender_start) * 1000)
    show_frame(age_frame)


gender_start = time.time()
tk.Button(gender_frame, text="确定", font=FONT_MAIN, command=submit_gender).pack(pady=10)
tk.Button(gender_frame, text="退出", font=FONT_MAIN, command=root.destroy).pack(side="bottom", pady=10)

# 3. 年龄信息
age_frame = tk.Frame(root)
tk.Label(age_frame, text="请选择您的年龄（周岁）范围：\n", font=FONT_BIG).pack(pady=20)
age_var = tk.StringVar(value="")
age_mark_labels = {}
age_groups = ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]


def set_age(group: str):
    age_var.set(group)
    for g, lbl in age_mark_labels.items():
        lbl.config(text="■" if g == group else "□")


for ag in age_groups:
    row = tk.Frame(age_frame)
    row.pack(anchor="w", padx=50, pady=6, fill="x")

    mark = tk.Label(row, text="□", font=FONT_MAIN, width=2)
    mark.pack(side="left")

    text_label = tk.Label(row, text=ag, font=FONT_MAIN, anchor="w", justify="left")
    text_label.pack(side="left", fill="x")

    age_mark_labels[ag] = mark

    mark.bind("<Button-1>", lambda e, v=ag: set_age(v))
    text_label.bind("<Button-1>", lambda e, v=ag: set_age(v))


def submit_age():
    if not age_var.get():
        return
    participant_info["age_group"] = age_var.get()
    participant_info["age_rt"] = int((time.time() - age_start) * 1000)
    show_frame(audio_test_frame)


age_start = time.time()
tk.Button(age_frame, text="确定", font=FONT_MAIN, command=submit_age).pack(pady=10)
tk.Button(age_frame, text="退出", font=FONT_MAIN, command=root.destroy).pack(side="bottom", pady=10)

# 4. 音频测试
audio_test_frame = tk.Frame(root)
tk.Label(audio_test_frame, text="音频测试", font=FONT_BIG).pack(pady=20)
tk.Label(
    audio_test_frame,
    text=(
        "点击下方按钮播放测试音频，\n"
        "调整音量至合适大小。\n"
        "确认可以清楚听到后再继续实验。"
    ),
    font=FONT_MAIN,
).pack(pady=10)


def play_test_sound():
    music_player.play_test_sound()


tk.Button(
    audio_test_frame,
    text="播放测试音频",
    font=FONT_MAIN,
    command=play_test_sound,
).pack(pady=5)
tk.Button(
    audio_test_frame,
    text="我已听到音频，进入下一步",
    font=FONT_MAIN,
    command=lambda: show_frame(start_frame),
).pack(pady=20)
tk.Button(audio_test_frame, text="退出", font=FONT_MAIN, command=root.destroy).pack(side="bottom", pady=10)

# 5. 正式开始提示
start_frame = tk.Frame(root)
tk.Label(start_frame, text="一切准备就绪！", font=FONT_BIG).pack(pady=20)
tk.Label(
    start_frame,
    text="点击开始正式答题后，实验将正式开始。\n实验正式开始后请连续作答，不要在中途关闭程序。",
    font=FONT_MAIN,
).pack(pady=10)
tk.Button(
    start_frame,
    text="开始正式答题",
    font=FONT_BIG,
    command=start_experiment,
).pack(pady=20)
tk.Button(start_frame, text="退出", font=FONT_MAIN, command=root.destroy).pack(side="bottom", pady=10)

root.mainloop()
