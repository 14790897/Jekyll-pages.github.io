---
title: 🚨 如何彻底从 Git 历史中移除敏感信息（以 secrets.h 为例）
date: 2025-09-30
categories: tech
share: true
comments: true
author_profile: true
related: true
---

在日常开发中，很多人都犯过一个“致命错误”——把密码、API Key、私钥等敏感信息直接提交到了 Git 仓库里。即便你后来删除了这个文件、甚至提交了 `.gitignore`，**这些秘密依然会留在 Git 的历史记录中**，任何人只要回溯旧提交都能看到。

本文就带你从零开始，彻底清理 Git 历史中的敏感文件（如 `secrets.h`），让它**彻底消失得无影无踪**。

---

## 🧨 一、为什么删掉文件还不够？

Git 是一个**快照型版本控制系统**，它不会“删除”文件，而是记录每一次的快照。
这意味着：

- 即便你在新提交中删除了 `secrets.h`，历史版本中依然存在它。
- 如果仓库是公开的，别人可以轻松 `git checkout` 到旧提交看到内容。
- 甚至搜索引擎、GitHub 历史浏览器也可能缓存了它。

👉 所以我们要做的，不是删除当前文件，而是**重写整个 Git 历史**。

---

## 🧰 二、使用 `git filter-repo` 清理历史

推荐使用官方的 [`git filter-repo`](https://github.com/newren/git-filter-repo) 工具，它比旧的 `filter-branch` 更快、更安全。

### 1️⃣ 安装

```bash
pip install git-filter-repo
```

---

## 🔥 三、在「干净克隆」上操作（推荐方式）

为了避免出错，建议**新克隆一份仓库副本**再操作：

```bash
git clone https://github.com/yourname/yourrepo.git clean-repo
cd clean-repo
```

然后执行：

```bash
git filter-repo --path secrets.h --invert-paths
```

如果是在子目录,请使用:

```bash
git filter-repo --path src/config/secrets.h --invert-paths
```

解释一下参数：

- `--path secrets.h`：要删除的文件路径（相对于仓库根目录）
- `--invert-paths`：删除指定路径，而不是保留

💡 如果文件不在根目录（例如 `src/config/secrets.h`），一定要写全路径：

```bash
git filter-repo --path src/config/secrets.h --invert-paths
```

---

## 🧹 四、清理遗留引用和对象（非常重要）

`filter-repo` 会生成新的提交树，但旧对象可能还“藏”在引用里，必须手动清理：

```bash
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## 🚀 五、强制推送覆盖远端历史

重写后的历史和原仓库完全不同，必须强制推送：

```bash
git remote add origin https://github.com/yourname/yourrepo.git
git push origin --force --all
git push origin --force --tags
```

⚠️ **注意**：如果你启用了“保护分支”，需要暂时关闭它或允许强推。

---

## 🛠 六、删除本地残留 + 添加到 `.gitignore`

即便历史清干净了，本地工作区可能还有文件副本。务必手动删除并忽略它：

```bash
rm secrets.h
echo "secrets.h" >> .gitignore
git add .gitignore
git commit -m "chore: ignore secrets.h"
git push
```

---

## 🔎 七、验证是否真的删除成功

执行以下命令来检查历史是否彻底清除：

```bash
git log --all --name-only -- "secrets.h"
git rev-list --objects --all | grep "secrets.h"
```

- ✅ 没有任何输出 → 成功！
- ❌ 有输出 → 说明历史中仍有残留，需要重新检查路径或重复清理。

---

## 🧠 八、如果敏感信息是“内容”而不是“文件”

有时我们并不是提交了文件，而是把密码写在代码里。这种情况可以用 `--replace-text`：

```bash
echo 'old_password==>REMOVED' > replace.txt
git filter-repo --replace-text replace.txt
```

这会把所有历史里匹配的字符串替换成 `REMOVED`。

---

## 📌 九、别忘了修改密码！

就算你成功删除了历史记录，**如果仓库曾经公开过，那些密码很可能已经泄露**。
**一定要立即更新 API Key、重置密码、吊销旧凭证！**

---

## 🧭 总结

| 步骤                                | 作用             |
| ----------------------------------- | ---------------- |
| 1️⃣ 备份或重新克隆仓库               | 避免误操作       |
| 2️⃣ `git filter-repo --invert-paths` | 删除敏感文件历史 |
| 3️⃣ 清理 refs/original & GC          | 移除残留对象     |
| 4️⃣ 强制推送                         | 覆盖远端旧历史   |
| 5️⃣ 删除本地文件并忽略               | 防止再次提交     |
| 6️⃣ 验证 & 修改密码                  | 最终安全收尾     |

---

🔐 **安全提示**
删除 Git 历史不是“后悔药”，只是“止血药”。敏感信息一旦被推送，**永远假设它已经泄露**，不要抱有侥幸心理。

---

📘 最后建议：

- 永远不要直接提交敏感文件，使用环境变量或 `.env` 管理。
- 使用 `.gitignore` 提前忽略机密文件。
- 开启 GitHub Secrets 或 CI/CD 环境变量机制。

---

✨ 结语：删除 Git 中的敏感信息并不难，难的是养成“不让它出现”的习惯。
