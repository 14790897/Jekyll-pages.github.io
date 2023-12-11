---
title: Python列出文件名 (Python list file names)
date: 2023-04-22
categories: python
---

要列出文件夹下所有文件名称，您可以使用`os`模块。`os.listdir()`函数会返回一个包含目录下所有文件和文件夹名称的列表。如果您还想进入子文件夹，可以使用`os.walk()`函数。以下是两个示例：

**示例1：使用os.listdir()**

```python
import os

def list_files(directory):
    for filename in os.listdir(directory):
        print(filename)

folder_path = 'your_directory_path'  # 请替换为您的文件夹路径
list_files(folder_path)
```

**示例2：使用os.walk()遍历子文件夹**

```python
import os

def list_files(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            print(os.path.join(root, filename))

folder_path = 'your_directory_path'  # 请替换为您的文件夹路径
list_files(folder_path)
```

请将`your_directory_path`替换为您要列出文件的实际文件夹路径。在示例2中，`os.path.join(root, filename)`会将根目录和文件名连接起来，以便您可以看到每个文件的完整路径。

## root, dirs, files分别是什么？举个例子

`root`, `dirs`, `files`是`os.walk()`函数返回的元组中的三个元素。当您遍历一个目录时，这三个变量将分别表示：

- `root`：当前遍历的文件夹的路径（字符串）。
- `dirs`：当前遍历的文件夹中所有子目录的名称列表（字符串列表）。
- `files`：当前遍历的文件夹中所有文件的名称列表（字符串列表）。

举个例子，假设我们有以下文件结构：

```
example_folder/
├── file1.txt
├── file2.txt
├── subfolder1/
│   ├── file3.txt
│   └── file4.txt
└── subfolder2/
    ├── file5.txt
    └── file6.txt
```

当您使用`os.walk()`遍历`example_folder`时，将得到以下结果：

1. 第一次迭代：
   - `root`: 'example\_folder/'
   - `dirs`: \['subfolder1', 'subfolder2']
   - `files`: \['file1.txt', 'file2.txt']
2. 第二次迭代：
   - `root`: 'example\_folder/subfolder1'
   - `dirs`: \[]
   - `files`: \['file3.txt', 'file4.txt']
3. 第三次迭代：
   - `root`: 'example\_folder/subfolder2'
   - `dirs`: \[]
   - `files`: \['file5.txt', 'file6.txt']

在每次迭代中，`os.walk()`返回当前文件夹的信息，并递归进入子文件夹。这样，您可以访问整个目录树中的所有文件和文件夹。

## 想输出相对当前folder_path的相对路径，怎么操作？

要输出相对于`folder_path`的相对路径，您可以使用`os.path.relpath()`函数。在以下示例中，我们使用`os.walk()`遍历文件夹，并输出相对于`folder_path`的相对路径：

```python
import os

def list_files(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, directory)
            print(relative_path)

folder_path = 'your_directory_path'  # 请替换为您的文件夹路径
list_files(folder_path)
```

`os.path.relpath()`函数接受两个参数：`path`和`start`。它会计算从`start`到`path`的相对路径。在这个例子中，`full_path`表示文件的完整路径，而`directory`表示`folder_path`。这样，我们可以输出文件相对于`folder_path`的路径。
