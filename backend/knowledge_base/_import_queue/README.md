# 知识导入队列

将原始文本文件放入此目录，然后运行批量导入命令。

## 三种导入方式

### 方式一：批量导入（推荐）

```bash
# 1. 把原始资料 (.txt/.md) 放入此目录
# 2. 运行批量导入
python -m scripts.import_knowledge --type method --batch
```

### 方式二：单个文件导入

```bash
python -m scripts.import_knowledge --input my_notes.txt --type method --name "粒子群算法"
```

### 方式三：从剪贴板/管道导入

```bash
cat my_paper.txt | python -m scripts.import_knowledge --type paper --stdin
```

## 支持的原始格式

- **.txt** — 纯文本描述、笔记、PDF 转文字
- **.md** — Markdown 格式的笔记

## 完整工作流程

1. 将原始资料（教材段落、论文摘要、笔记）粘贴到 .txt/.md 文件中
2. 放入此目录
3. 运行批量导入命令 → LLM 自动提取结构 → 生成规范 YAML
4. 处理完成的源文件自动删除
5. 运行 `python -m app.knowledge.indexer --incremental` 更新向量索引
6. 在 `/knowledge` 页面验证可搜索到新内容

## 示例

创建 `粒子群算法.txt`:

```
粒子群优化算法(PSO)是一种基于群体智能的启发式优化算法。
由Kennedy和Eberhart于1995年提出，灵感来源于鸟群觅食行为。

每个粒子代表一个候选解，通过跟踪个体最优位置和全局最优位置
来更新自己的位置和速度。

速度更新公式: v_i = w*v_i + c1*r1*(pbest_i - x_i) + c2*r2*(gbest - x_i)

适用场景: 连续优化、多峰函数优化、神经网络训练
不适用: 需要精确解、离散组合优化(需改进的离散PSO)
常见误用: 参数设置不当导致早熟收敛

Python实现:
import numpy as np
def pso(objective_func, bounds, n_particles=30, max_iter=100):
    ...
```
