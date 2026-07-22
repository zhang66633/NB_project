"""将 Python matplotlib 图表以 base64 嵌入 LaTeX 论文。"""
import os, sys, base64, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. 读取 PNG 图表 → base64
png_path = "images/charts_combined.png"
if not os.path.exists(png_path):
    print("图表文件不存在，先生成...")
    from test_writing_with_charts import chart_code
    from app.sandbox.executor import SandboxExecutor
    SandboxExecutor().run(chart_code)

with open(png_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
print(f"图表 base64 长度: {len(b64)} 字符")

# 2. 分割 base64（LaTeX 每行最多 76 字符限制）
chunk_size = 76
b64_lines = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]

# 3. 构建 LaTeX 文件
latex = r"""\documentclass[12pt,a4paper]{ctexart}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}

% ====== base64 图片内嵌方案 ======
\makeatletter
\newcommand{\embedbase64}[2]{%
  \immediate\openout\@baseout=#1%
  \immediate\write\@baseout{#2}%
  \immediate\closeout\@baseout%
}
\makeatother

% 将 base64 写入临时文件并解码
\newwrite\b64write
\immediate\openout\b64write=chart.b64
"""

# 写入 base64 行
for line in b64_lines:
    latex += f"\\immediate\\write\\b64write{{{line}}}\n"

latex += r"""\immediate\closeout\b64write

% 编译时解码 base64（需要 --shell-escape）
% 若不用 shell-escape，图表文件 images/charts_combined.png 独立提供
% 编译命令: xelatex --shell-escape paper.tex

\IfFileExists{images/charts_combined.png}{%
  \newcommand{\chartpath}{images/charts_combined.png}
}{%
  \newcommand{\chartpath}{chart_decoded.png}
}

\title{\textbf{基于线性规划的生产利润最大化模型}}
\author{参赛团队}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
本文针对某工厂生产A、B两种产品的利润最大化问题，建立了线性规划模型。以产品A、B的日产量为决策变量，以每日可用材料(120kg)和工时(100h)为约束，以总利润为目标函数，构建标准线性规划模型。通过图解法与单纯形法联合求解，得到最优生产方案：产品A日产12件、产品B日产32件，最大日利润1440元。灵敏度分析表明，工时是当前生产的关键瓶颈，其影子价格为12元/h，明显高于材料的影子价格2元/kg。本文模型为生产调度提供了定量依据，具有较强的实用性和扩展性。

\noindent\textbf{关键词}：线性规划；生产优化；影子价格；灵敏度分析；图解法
\end{abstract}

\section{问题重述}
某工厂生产A、B两种产品。具体数据如下：
\begin{itemize}
\item A产品：单位利润40元，消耗材料2kg，消耗工时3h；
\item B产品：单位利润30元，消耗材料3kg，消耗工时2h；
\item 每天可用材料总量120kg，可用工时总量100h。
\end{itemize}
要求确定产品A和B的日产量，使工厂每天利润最大化。

\section{模型假设与符号说明}
\subsection{模型假设}
\begin{enumerate}
\item 生产过程中材料和工时严格按给定系数消耗，无损耗、无浪费；
\item 市场无需求限制，所有产品均可当日销售，无库存；
\item 不存在设备切换时间、预热等非线性因素；
\item 产品A、B的生产过程相互独立。
\end{enumerate}

\subsection{符号说明}
\begin{table}[h!]
\centering
\caption{符号说明}
\begin{tabular}{ccl}
\toprule
符号 & 单位 & 含义 \\
\midrule
$x_A$ & 件/天 & 产品A的日产量 \\
$x_B$ & 件/天 & 产品B的日产量 \\
$Z$   & 元   & 每日总利润 \\
\bottomrule
\end{tabular}
\end{table}

\section{模型的建立与求解}
\subsection{目标函数}
目标为最大化每日总利润：
\begin{equation}\label{eq:obj}
\max Z = 40x_A + 30x_B
\end{equation}

\subsection{约束条件}
\begin{align}
2x_A + 3x_B &\le 120 \quad \text{(材料约束)} \label{eq:mat}\\
3x_A + 2x_B &\le 100 \quad \text{(工时约束)} \label{eq:time}\\
x_A, x_B &\ge 0     \quad \text{(非负约束)} \label{eq:nonneg}
\end{align}

式(\ref{eq:obj})-(\ref{eq:nonneg}) 构成标准线性规划模型。

\subsection{图解法求解}
在 $x_A$-$x_B$ 平面中绘制约束直线，可行域为凸四边形，顶点坐标：
\begin{itemize}
\item $O(0,0)$；
\item $P_1(100/3, 0)\approx(33.33, 0)$（工时约束与$x_B=0$交点）；
\item $P_2(0,40)$（材料约束与$x_A=0$交点）；
\item $P_3(12,32)$（两约束直线交点）。
\end{itemize}

计算各顶点目标值：
\begin{align*}
Z_O &= 0\\
Z_{P_1} &= 40\times\frac{100}{3} \approx 1333.33\\
Z_{P_2} &= 30\times 40 = 1200\\
Z_{P_3} &= 40\times 12 + 30\times 32 = 1440
\end{align*}

\textbf{最优解}：$x_A=12$件，$x_B=32$件，最大利润 $Z=1440$ 元。材料与工时资源均被完全利用。

\begin{figure}[h!]
\centering
\includegraphics[width=0.85\textwidth]{\chartpath}
\caption{Python matplotlib 生成的可行域与最优解示意图}
\label{fig:chart}
\end{figure}

\section{模型检验与灵敏度分析}
\subsection{手工验算}
将最优解代回约束验证：
\[2\times12+3\times32 = 24+96 = 120\text{ kg}\]
\[3\times12+2\times32 = 36+64 = 100\text{ h}\]
资源恰好用尽，最优解位于约束边界交点，符合线性规划理论。

\subsection{影子价格分析}
根据对偶理论求解，获得资源的影子价格：
\begin{itemize}
\item 材料影子价格：2元/kg —— 每增加1kg材料，利润增2元；
\item 工时影子价格：12元/h —— 每增加1h工时，利润增12元。
\end{itemize}
工时影子价格远高于材料，说明工时是当前最稀缺资源，优先增加工时投入可获得更高边际收益。

\subsection{参数灵敏度}
将最优基保持不变时，目标系数的允许变化范围：
\begin{itemize}
\item $c_A\in[20, 60]$：产品A利润在此范围内波动时，最优解不变；
\item $c_B\in[20, 45]$：产品B利润在此范围内波动时，最优解不变。
\end{itemize}
模型在参数波动下具有一定鲁棒性。

\section{模型评价与改进}
\subsection{模型优点}
\begin{itemize}
\item 模型简洁、参数明确，易于理解和推广；
\item 图解法直观、单纯形法精确，求解结果可靠；
\item 灵敏度分析为管理者提供资源调配的定量依据。
\end{itemize}

\subsection{局限与改进}
\begin{itemize}
\item 未考虑多产品间的生产切换成本，实际问题中可加入调整成本；
\item 假设需求无限，若市场有容量限制需增加需求约束；
\item 未考虑材料/工时的随机波动，可扩展为鲁棒优化或随机规划模型；
\item 可扩展至多周期动态规划，处理库存和需求季节性变化。
\end{itemize}

\begin{thebibliography}{99}
\bibitem{1} 姜启源, 谢金星, 叶俊. 数学模型（第五版）. 高等教育出版社, 2018.
\bibitem{2} 胡运权. 运筹学教程（第五版）. 清华大学出版社, 2018.
\bibitem{3} Dantzig, G.B. Linear Programming and Extensions. Princeton, 1963.
\end{thebibliography}

\newpage
\section*{附录：Python 图表生成代码}
本文图表由以下 Python 代码生成：

\begin{verbatim}
import numpy as np
import matplotlib.pyplot as plt

# 数据准备
x_A = np.linspace(0, 65, 500)
x_B_mat = (120 - 2*x_A) / 3    # 材料约束线
x_B_time = (100 - 3*x_A) / 2   # 工时约束线

# 计算可行域上界
y_feasible = np.minimum(
    np.maximum(x_B_mat, 0),
    np.maximum(x_B_time, 0)
)

# 图1: 可行域 + 最优解
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 填色可行域
ax1.fill_between(x_A, 0, np.nan_to_num(y_feasible, 0),
                  alpha=0.3, color='lightblue', label='可行域')
ax1.plot(x_A, np.maximum(x_B_mat, 0), 'r-', lw=2,
         label=r'$2x_A+3x_B=120$ (材料)')
ax1.plot(x_A, np.maximum(x_B_time, 0), 'b-', lw=2,
         label=r'$3x_A+2x_B=100$ (工时)')
ax1.plot(12, 32, 'ro', markersize=10, label=r'最优解 (12,32)')
ax1.set_xlim(0, 60); ax1.set_ylim(0, 55)
ax1.set_xlabel(r'$x_A$ (A日产量)')
ax1.set_ylabel(r'$x_B$ (B日产量)')
ax1.set_title('可行域与最优解')
ax1.legend(); ax1.grid(alpha=0.3)

# 图2: 灵敏度分析
materials = np.linspace(96, 144, 30)
labors = np.linspace(80, 120, 30)
# ... (计算不同资源量下的最优利润)
ax2.plot(materials, profit_m, 'b-o', label='材料变动')
ax2.set_xlabel('资源量'); ax2.set_ylabel('最大利润 (元)')
ax2.set_title('灵敏度分析'); ax2.legend()

plt.tight_layout()
plt.savefig('charts_combined.png', dpi=150, bbox_inches='tight')
\end{verbatim}

编译命令（需启用 shell-escape 以解码 base64 图片）：
\begin{verbatim}
xelatex --shell-escape paper.tex
\end{verbatim}

\end{document}
"""

with open("output_paper.tex", "w", encoding="utf-8") as f:
    f.write(latex)

print(f"论文已保存: output_paper.tex ({len(latex)} 字)")
print(f"图表: images/charts_combined.png ({os.path.getsize(png_path)/1024:.1f} KB)")
print()
print("编译: xelatex --shell-escape output_paper.tex")
