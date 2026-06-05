import csv

def save_participant_info(participant_id, info, filename="participants.csv"):
    """保存参与者基本信息（性别、年龄段及反应时）到 CSV。"""
    headers = ["participant_id", "gender", "gender_rt_ms", "age_group", "age_group_rt_ms"]
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow([
            participant_id,
            info.get("gender"),
            info.get("gender_rt"),
            info.get("age_group"),
            info.get("age_rt")
        ])

def save_round_map(participant_id, rounds, filename="round_map.csv"):
    """保存轮次与音乐的对应关系到 CSV，每位被试 5 行数据。"""
    headers = ["participant_id", "round_index", "music_id"]
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for round_info in rounds:
            writer.writerow([participant_id, round_info["round_index"], round_info["music_id"]])

def save_trials(participant_id, trial_results, filename="trials.csv"):
    """保存题目作答结果到 CSV，每位被试 10 行数据。"""
    headers = [
        "participant_id", "question_id", "is_formal", "question_type", "round_index",
        "position_in_round", "rt_initial_ms", "conf_initial_1_5", "conf_rt_ms",
        "is_correct", "selected_option", "post_shown", "probe_order", "probe_delay_ms",
        "conf_post_original_1_5", "conf_post_original_ms", "changed_answer",
        "changed_answer_content", "changed_answer_ms", "music_id"
    ]
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        # trial_results 是以 question_id 为 key 的 dict
        rows = list(trial_results.values())
        rows.sort(key=lambda r: (r["round_index"], r["position_in_round"]))
        for res in rows:
            is_correct = res.get("is_correct")
            row = [
                participant_id,
                res.get("question_id"),
                res.get("is_formal"),
                res.get("question_type"),
                res.get("round_index"),
                res.get("position_in_round"),
                res.get("rt_initial_ms", "NA"),
                res.get("conf_initial", "NA"),
                res.get("conf_initial_rt_ms", "NA"),
                is_correct if is_correct is not None else "NA",
                res.get("answer_choice", "NA"),           # 原始选择的选项
                res.get("post_shown", 0),                # 是否进入追问（正式题需要追问为 1）
                res.get("probe_order", "NA"),
                res.get("probe_delay_ms", "NA"),
                res.get("conf_post_original", "NA"),
                res.get("conf_post_original_ms", "NA"),
                res.get("changed_answer", "NA"),
                res.get("changed_answer_content", "NA"),
                res.get("changed_answer_ms", "NA"),
                res.get("music_id")
            ]
            writer.writerow(row)

def save_music_ratings(participant_id, music_ratings, rounds, filename="music_ratings.csv"):
    """保存音乐主观评价结果到 CSV，每位被试 5 行数据（每首音乐，包括空白条件）。"""
    headers = ["participant_id", "music_id", "round_index", "arousal_1_5", "valence_1_5", "liking_1_5", "familiarity_1_5", "rating_order"]
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        # 按照《Procedure.docx》要求的字段顺序输出
        for round_info in sorted(rounds, key=lambda r: r["round_index"]):
            mid = round_info["music_id"]
            ridx = round_info["round_index"]
            if mid in music_ratings:
                ratings = music_ratings[mid]
                writer.writerow([
                    participant_id,
                    mid,
                    ridx,
                    ratings.get("arousal", "NA"),
                    ratings.get("valence", "NA"),
                    ratings.get("liking", "NA"),
                    ratings.get("familiarity", "NA"),
                    ratings.get("rating_order", "NA")
                ])
            else:
                # 空白音乐，无评分（评分字段填 NA）
                writer.writerow([
                    participant_id,
                    mid,
                    ridx,
                    "NA", "NA", "NA", "NA", "NA"
                ])
