---
title: windows下vscode使用latex教程
date: 2024-10-14
categories: tech
share: true
comments: true
author_profile: true
related: true
---

1. 安装 miktex
   https://miktex.org/download
   测试：
   xelatex --version

2. 安装 perl
   https://strawberryperl.com
   测试：
   perl --version

3. VS Code 安装插件
   在 VS Code 中按 Ctrl + Shift + X 打开扩展市场，搜索 LaTeX Workshop，点击 安装。
  
4. 配置使用 xelatex 而不是 pdflatex
   创建.vscode/settings.json
   内容：

   ```json
   {
     "latex-workshop.latex.tools": [
       {
         "name": "latexmk",
         "command": "latexmk",
         "args": [
           "-xelatex",
           "-synctex=1",
           "-interaction=nonstopmode",
           "-file-line-error",
           "-outdir=%OUTDIR%",
           "%DOC%"
         ]
       }
     ]
   }
   ```

5. 编写和编译 LaTeX 文件
   新建一个 .tex 文件，例如 main.tex。
   输入以下示例代码：

  ```latex
  \documentclass{article}
  \usepackage{xeCJK}  % 支持中文
  \setCJKmainfont{SimSun}  % 使用宋体
  \title{我的第一篇 LaTeX 文档}
  \author{作者姓名}
  \date{\today}

  \begin{document}
  \maketitle
  \section{引言}
  这是我的第一篇 LaTeX 文档。
  \end{document}
  ```

  按 Ctrl + S 保存文件，VS Code 将自动编译并生成 PDF。

## 参考内容
https://stackoverflow.com/questions/56109128/enable-xelatex-in-latex-workshops-for-visual-studio-code
