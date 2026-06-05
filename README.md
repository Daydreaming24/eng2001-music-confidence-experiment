# ENG2001 Research Project / ENG2001 研究项目

本仓库是一个 ENG2001 小型研究项目的实验程序与文档归档。项目关注古典器乐的主观情绪维度如何影响决策自信，尤其是音乐环境下的即时自信，以及之后在无音乐环境中重新面对原决策时的自信稳定性。

This repository archives the experimental program and documentation for a small ENG2001 research project. The project examines how subjective emotional dimensions of classical instrumental music influence decision confidence, especially immediate confidence during music exposure and confidence stability when participants later reconsider their decisions in silence.

研究已经结束；本 README 主要用于说明项目目的、实验程序、文件结构与数据输出格式。

The study has been completed. This README explains the project purpose, experimental procedure, file structure, and data outputs.

## 项目概览 / Project Overview

本研究以线上实验方式收集中国成年参与者的数据。参与者在不同音乐条件下完成一组选择题，并在每次作答后报告自信程度。随后，程序会在无音乐环境中对部分题目呈现与原答案相反或不利的信息，让参与者再次评价对原答案的自信，并决定是否修改答案。实验最后，参与者会对实验中听到的音乐进行主观评分。

This study collected data from Chinese adult participants through an online experiment. Participants answered a set of multiple-choice questions under different music conditions and reported their confidence after each decision. Later, in a silent environment, the program presented counter-attitudinal or unfavorable information for selected questions, asked participants to reassess their confidence in the original answer, and recorded whether they changed their answer. At the end of the experiment, participants rated the music they had heard.

本研究的主要结论是：高唤醒度音乐与更高的即时自信趋势相关，并且与后续无音乐追问阶段中更稳定的自信表现相关；音乐效价、喜爱度和熟悉度没有显示出稳定的显著效应。

The main finding of this study is that high-arousal music was associated with a trend toward higher immediate confidence and with more stable confidence in the later silent follow-up phase. Valence, liking, and familiarity did not show reliable significant effects.

## 研究设计 / Research Design

实验材料包含 8 段古典器乐音乐刺激，按唤醒度和效价划分为 4 个象限，每个象限包含 2 首音乐。每位参与者会从每个象限随机听到 1 首音乐，并额外经历 1 个无音乐条件，因此共有 5 个实验轮次。

The stimuli include 8 classical instrumental music excerpts, divided into 4 quadrants by arousal and valence, with 2 excerpts in each quadrant. For each participant, the program randomly selects 1 excerpt from each quadrant and adds 1 no-music condition, resulting in 5 experimental rounds.

题库包含 10 道选择题：

The question pool contains 10 multiple-choice questions:

- 5 道正式题：用于研究分析，包含客观题与主观题，并可能进入追问环节。
- 5 formal questions: used for analysis, including both objective and subjective questions, with possible follow-up prompts.
- 5 道干扰题：用于降低参与者对研究目的的直接察觉。
- 5 filler questions: used to reduce participants' direct awareness of the research purpose.

每个轮次包含 2 道题：1 道正式题和 1 道干扰题。题目顺序、音乐条件顺序、正式题顺序和干扰题顺序都会随机化。

Each round contains 2 questions: 1 formal question and 1 filler question. The program randomizes question order, music-condition order, formal-question order, and filler-question order.

## 实验流程 / Experimental Procedure

1. 欢迎页与实验说明 / Welcome page and experiment instructions
2. 收集基本人口学信息：性别、年龄组 / Basic demographic information: gender and age group
3. 音频测试与音量确认 / Audio test and volume confirmation
4. 正式答题：在音乐或无音乐条件下完成题目，并记录答案、反应时和即时自信度 / Main task: participants answer questions under music or no-music conditions; the program records answers, response time, and immediate confidence
5. 追问环节：在无音乐环境下呈现部分题目的提示信息，记录追问后自信度和是否改答案 / Follow-up phase: selected prompts are shown in silence; the program records post-prompt confidence and whether the participant changes the answer
6. 音乐评分：对听过的音乐分别评价唤醒度、效价、喜爱度和熟悉度 / Music rating: participants rate arousal, valence, liking, and familiarity for the music they heard
7. 自动导出 CSV 数据表 / Automatic CSV data export

## 仓库结构 / Repository Structure

```text
.
├── README.md
├── LICENSE
├── docs/
│   ├── papers/
│   │   ├── research_paper_draft.docx
│   │   └── 124090033_paper.doc
│   └── procedure/
│       └── Procedure.docx
└── src/
    ├── main.py
    ├── questions_data.py
    ├── question_manager.py
    ├── data_logger.py
    ├── music_player.py
    ├── ExperimentApp.spec
    ├── images/
    └── music_files/
```

主要文件说明 / Main file descriptions:

- `src/main.py`：Tkinter 实验主程序，负责界面、随机化、题目呈现、追问流程和数据保存。 / Main Tkinter experiment program, handling the interface, randomization, question presentation, follow-up flow, and data saving.
- `src/questions_data.py`：10 道实验题及追问材料。 / The 10 experiment questions and follow-up materials.
- `src/music_player.py`：音乐播放和图片资源路径管理。 / Music playback and image-resource path management.
- `src/data_logger.py`：导出实验结果 CSV。 / CSV export for experiment results.
- `src/ExperimentApp.spec`：PyInstaller 打包配置。 / PyInstaller packaging configuration.
- `docs/procedure/Procedure.docx`：原始实验思路、实验流程和数据表字段设计说明。 / Original experimental idea, procedure notes, and data-field design.
- `docs/papers/`：研究论文相关文档。 / Research paper documents.
- `LICENSE`：本项目代码的 MIT 许可证。 / MIT License for the project code.

## 运行方式 / How to Run

当前实验程序主要适配 Windows 平台。界面字体固定使用 Windows 常见的 `SimSun`（宋体）；在 WSL/Linux 环境中运行时，若系统缺少对应中文字体，Tkinter 界面可能会把中文显示为 `\uXXXX` 形式的 Unicode 转义字符串。

The current experiment program is primarily designed for Windows. The interface uses `SimSun`, a common Windows Chinese font. When running under WSL/Linux, Tkinter may display Chinese text as `\uXXXX` Unicode escape strings if the corresponding Chinese font is unavailable.

### 从源码运行 / Running from Source

建议在 Windows 环境中使用 Python 3，并安装以下依赖：

Python 3 on Windows is recommended. Install the required dependencies:

```bash
pip install pillow pygame
```

然后运行：

Then run:

```bash
python src/main.py
```

### 本地打包 / Local Packaging

为避免上传超过 GitHub 单文件限制的构建产物，仓库不保留预打包的 `src/dist/ExperimentApp.exe`。如需 Windows 可执行文件，可以在本地安装 PyInstaller 后重新打包：

To avoid committing build artifacts that exceed GitHub's single-file size limit, this repository does not keep the prebuilt `src/dist/ExperimentApp.exe`. If a Windows executable is needed, rebuild it locally with PyInstaller:

```bash
pip install pyinstaller pillow pygame
cd src
pyinstaller ExperimentApp.spec
```

生成的程序会位于 `src/dist/ExperimentApp.exe`。

The generated program will be available at `src/dist/ExperimentApp.exe`.

## 输出数据 / Data Outputs

程序结束时会生成以下 CSV 文件：

At the end of the program, the following CSV files are generated:

- `participants.csv`：参与者 ID、性别、年龄组及对应反应时。 / Participant ID, gender, age group, and corresponding response times.
- `round_map.csv`：每位参与者 5 个轮次对应的音乐条件。 / The music condition assigned to each of the 5 rounds for each participant.
- `trials.csv`：每道题的作答、反应时、即时自信、追问后自信、是否改答案等试次级数据。 / Trial-level data, including answer choice, response time, immediate confidence, post-follow-up confidence, and whether the answer was changed.
- `music_ratings.csv`：参与者对音乐的唤醒度、效价、喜爱度和熟悉度评分。 / Participant ratings of music arousal, valence, liking, and familiarity.

原始实验思路和各字段的详细设计见 `docs/procedure/Procedure.docx`。

The original experimental idea and detailed field design are available in `docs/procedure/Procedure.docx`.

## 媒体素材说明 / Media Materials

本项目中的音乐和图片素材均来源于共有领域。具体素材来源链接已记录在论文文档中，尤其是 `docs/papers/research_paper_draft.docx` 的试题附录部分。

All music and image materials used in this project are from the public domain. Specific source links are recorded in the paper documents, especially in the question appendix of `docs/papers/research_paper_draft.docx`.

当前程序使用的图片资源位于 `src/images/`，音乐资源位于 `src/music_files/`。这些文件仅用于本课程研究项目和实验复现说明。

The image resources currently used by the program are stored in `src/images/`, and the music resources are stored in `src/music_files/`. These files are included only for this course research project and experiment-reproduction documentation.

## 许可证 / License

本项目代码采用 MIT License 授权，详见 `LICENSE`。

The source code in this repository is licensed under the MIT License. See `LICENSE` for details.

音乐和图片素材均来源于共有领域，具体来源链接记录在论文文档中。研究论文和实验流程文档作为课程研究归档材料保留；如引用或复用其中的研究内容，请注明作者与项目来源。

Music and image materials are from the public domain, with source links documented in the paper files. The research paper and procedure documents are included as academic/course archive materials; if you cite or reuse the research content, please attribute the author and project source.

## 研究文档 / Research Documents

完整研究背景、方法、结果、讨论和参考文献见：

For the full research background, methods, results, discussion, and references, see:

- `docs/papers/research_paper_draft.docx`
- `docs/papers/124090033_paper.doc`

其中论文记录了研究问题、统计分析思路、主要发现，以及实验题目和媒体素材来源。

The paper documents record the research questions, statistical-analysis approach, main findings, experiment questions, and media-source links.
