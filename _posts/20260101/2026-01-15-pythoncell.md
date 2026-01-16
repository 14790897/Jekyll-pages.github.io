---
title: VS Code 隐藏技巧：不用 Jupyter Notebook 也能拥有交互式体验
date: 2026-01-14
categories:
  - finance
tags:
  - NASDAQ100
  - QQQM
  - QDII
  - 定投策略
---

你有没有这样的经历？

当你想测试一段简单的 Python 代码（比如测试一个 API，或者调试一个正则）时，你通常会怎么做？

1. 新建一个 `test.py` 或者 `temp.py`。
2. 输入代码。
3. 打开终端，输入 `python test.py`。
4. 发现报错了，修改代码，再运行一遍。
5. 测试完后，看着满桌面的垃圾文件陷入沉思……

或者，你可能喜欢用 Jupyter Notebook (`.ipynb`)，但他需要启动服务，而且 `.ipynb` 文件在 Git 版本控制里简直是噩梦。

今天介绍一个 VS Code 自带的“魔法指令”，让你在普通的 `.py` 文件里，也能拥有 Jupyter 般的交互式体验。它就是 —— **`# %%`**。

### 什么是 `# %%`？

这其实是 VS Code 对 **Python Interactive Window (交互式窗口)** 的特殊标记。

它的原理很简单：**只要你在普通的 Python 代码中输入 `# %%`，VS Code 就会把这就行代码及其下方的代码识别为一个“单元格 (Cell)”。**

这就好比在你的代码里划了一道“起跑线”。

### 如何使用？

1. 随便打开一个 `.py` 文件（我通常会常备一个 `draft.py` 草稿本）。
2. 在代码上方输入 `# %%`（注意中间有个空格）。
3. 你会发现代码上方突然多出了一行灰色的文字：`Run Cell | Run Below | Debug Cell`。
4. 点击 **Run Cell**，或者直接按快捷键 **`Shift + Enter`**。

神奇的事情发生了：你的 VS Code 会在右侧弹出一个独立的窗口，立刻显示这段代码的运行结果！

```python
# %%
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.show() 
# 点击 Run Cell，右边直接出图！

```

### 为什么要用它？三大核心优势

#### 1. 变量是“活”的 (State Retention)

这是它比终端运行强一万倍的地方。
在终端里，每次运行 `python test.py`，程序跑完就退出了，内存里的变量全部清空。
而在交互式窗口里，**变量是常驻内存的**。

* 你可以在第一个 Cell 里加载一个 500MB 的数据集（耗时 10秒）。
* 然后在第二个 Cell 里随意分析这个数据。
* **你不需要每次都重新加载那 500MB 的数据！**

#### 2. “草稿本”神技

你可以把几十个不相关的测试代码写在同一个文件里，用 `# %%` 隔开。

* 上面的 Cell 测爬虫。
* 中间的 Cell 算算法。
* 下面的 Cell 画图。
它们互不干扰，想跑哪段点哪段。你的项目文件夹里再也不会出现 `test1.py`, `test2.py`, `test_final.py` 这种垃圾文件了。

#### 3. 可视化神器

它完美支持 `pandas` 的表格显示和 `matplotlib` 的绘图。不需要 `plt.show()` 弹窗，图表直接嵌在右边的窗口里，还可以缩放、保存，体验和 Jupyter Notebook 一模一样。

### 避坑指南

当你第一次点击 Run Cell 时，VS Code 可能会右下角弹窗提示：

> *"Running cells with 'Python 3.xx' requires the ipykernel package."*

别慌，这是因为 Python 原生不懂什么是 Cell，它需要一个“翻译官”。**直接点击 Install (安装)**，几秒钟后就能用了。

另外，在这个交互窗口的顶部，你可以像切换电视频道一样**切换 Python 内核**（比如从 3.13 切回 3.12），非常方便。

### 总结

`# %%` 是我认为 VS Code Python 插件里被最严重低估的功能。它完美平衡了 `.py` 文件的工程便利性和 Jupyter Notebook 的探索灵活性。

从今天起，在该建 `test.py` 之前，先试试在你的代码里敲下这四个字符：`#`、`空格`、`%`、`%`。

---

