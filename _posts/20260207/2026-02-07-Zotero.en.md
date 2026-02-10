---
categories:
- tech
date: 2026-02-07
tags:
- Word技巧
- Zotero
- 论文写作
- 参考文献格式
- 学术写作
title: 'Word + Zotero Advanced: How to Make Your Bibliography Formatting Stick (Even
  After Refreshing)'
---

Have you ever experienced that **moment of despair**: After painstakingly adjusting the font, spacing, and finally managing to change those dozens of bibliography entries from bizarre "Center Alignment" to neat "Left Alignment," you insert a new citation in the text and carelessly click the **`Refresh`** button in the Zotero plugin bar (or Zotero auto-refreshes).

**"Snap!"**
You're back to square one. All your references revert to that ugly default style (e.g., all centered, or the font suddenly enlarges).

Did you think it was a Zotero bug? No, this actually means you haven't correctly utilized Word's **"Styles."** Today, I'll teach you a trick to put a "permanent lock" on your bibliography so it maintains perfect formatting no matter how many times you refresh.

#### ❌ Why Manual Edits Don't Work

When Zotero generates the bibliography list in Word, it doesn't just paste plain text. It calls upon a built-in Word style, usually named **"Bibliography"** (English version) or **"书目"** (Chinese version).

* **Manual modification** (like selecting the text with your mouse and clicking left-align) is like applying "makeup."
* **Clicking Refresh** is Zotero regenerating the list according to the style definition—it's "removing the makeup."

If the style named "Bibliography" is inherently defined as "Centered," then every time you refresh, Zotero will faithfully execute the "Center" command. **Therefore, we must modify the "Style" itself, not the text.**

#### ✅ The Root Solution: Three Steps to Modify the "Bibliography" Style

Don't bother searching through the crowded Styles ribbon at the top of Word. Let's use the **"God View"** approach instead.

**Step One: Summon the "Apply Styles" Window**
Select any one of your bibliography entries and press the keyboard shortcut:
👉 **`Ctrl` + `Shift` + `S`**

A small floating window titled [Apply Styles] will pop up.
Note the name in the box; it will usually display **"Bibliography"** (or "书目"). This is the mastermind controlling all your references.

**Step Two: Enter Modification Mode**
In this small window, click the **"Modify"** button.
The window that appears now is the "supreme law" governing your formatting.

**Step Three: Correct "Centering" and Other Quirks**
In this window, you need to check the following key points:

1. **Alignment (The Culprit)**:
Look at the icon area in the middle. If the **"Center"** button is pressed, quickly change it to **"Align Left"** (or Justify). This is why your bibliography jumps to the center every time you refresh.
2. **Font and Line Spacing**:
Set the font (e.g., Times New Roman, 10pt/12pt) and line spacing required by your institution here.
3. **Hanging Indent**:
In the [Format] menu, select **"Paragraph,"** and in the window that pops up, find **"Special"** under Indentation, select **"Hanging,"** and set an appropriate indent value (usually 0.5 inches or 1.27 cm).
4. **Don't forget to click "OK."**

#### 💡 Witness the Miracle

Now, return to your paper.

1. Mess up the bibliography formatting randomly.
2. Click the Zotero **`Refresh`** button.
3. You will find that the formatting is **rock solid**, maintaining the perfect appearance you just set.


---

### Summary

Do not try to fight Zotero's automation with manual formatting. **Fight magic with magic**—directly modifying the **"Bibliography"** style is the correct way to handle academic writing.

Spend your time writing code and conducting experiments; this small formatting task only needs to be set up once!