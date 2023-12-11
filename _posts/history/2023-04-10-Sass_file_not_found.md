---
layout: custom-post
categories: tech
title: Jekyll/CSS/HTML bug
date: 2023-04-10
---

# Sass file not found

```
Warning: 1 repetitive deprecation warnings omitted.
Run in verbose mode to see all warnings.
                    done in 0.985 seconds.
 Auto-regeneration: enabled for 'E:/program/git/14790897.github.io'
    Server address: http://127.0.0.1:4000/
  Server running... press ctrl-c to stop.
  [2023-04-10 09:53:39] ERROR `/assets/css/custom.scss' not found.
```

## 我明明有/assets/css/custom.scss这个文件，为什么没有找到呢？


#### 首先让我们看看引用路径是否正确，以下是错误示范
<link rel="stylesheet" href="{{ '/assets/css/custom.scss' | relative_url }}">

这是一个HTML代码片段，它使用Jekyll的Liquid模板引擎将`custom.scss`文件引入到您的`custom-post.html`模板中。让我们逐行分析：

1. `<link rel="stylesheet" href="{{ '/assets/css/custom.scss' | relative_url }}">`

   - `<link>`：HTML的`<link>`元素用于在当前文档与外部资源（例如样式表）之间建立关联。在这种情况下，它用于引入一个CSS样式表。
   - `rel="stylesheet"`：`rel`属性定义了当前文档与链接资源之间的关系类型。在这里，它表示链接的资源是一个样式表。
   - `href="{{ '/assets/css/custom.scss' | relative_url }}"`：`href`属性指定链接资源的URL。在这里，我们使用了一个Liquid模板表达式来动态生成URL。
     - `'/assets/css/custom.scss'`：这是`custom.scss`文件在项目中的相对路径。
     - `| relative_url`：这是一个Liquid过滤器，它将输入的路径转换为相对于当前站点的URL。这对于确保链接在站点的任何部署环境中都能正常工作非常有用。

### 问题所在

这段代码的作用是将`custom.scss`样式表引入到`custom-post.html`模板中。但是，需要注意的是，这里直接引入了`.scss`文件，浏览器通常无法直接解析Sass文件（`.scss`）。正确的做法是将`.scss`文件编译成`.css`文件后再引入。

为了解决这个问题，您可以在项目的`/assets/css`目录中创建一个名为`custom.scss`的新文件，并在文件顶部添加以下内容：

```
---
---
```

这是一个空的YAML前置声明，它告诉Jekyll处理这个`.scss`文件并将其编译为一个`.css`文件。接下来，在`custom-post.html`文件中，将引用的文件扩展名从`.scss`更改为`.css`：

```
<link rel="stylesheet" href="{{ '/assets/css/custom.css' | relative_url }}">
```

现在，当您运行Jekyll并生成站点时，`custom.scss`文件将被编译为`custom.css`文件，然后在`custom-post.html`模板中正确引用。

### 原因在于编译过程中scss文件转变成了css文件，而我的引用却是xxx.scss！！！！

恭喜您找到了问题所在！正如我之前提到的，浏览器需要CSS文件来应用样式。在部署到Web服务器之前，SCSS文件需要被编译成CSS文件。确保在HTML文件中引用编译后的CSS文件，而不是原始的SCSS文件。这样，您的网站就可以正确地显示和应用样式了。

例如，在您的HTML或模板文件中，您应该这样引用CSS文件：

```html
<link rel="stylesheet" href="{{ '/assets/css/custom.css' | relative_url }}">
```

请注意，这里引用的是`custom.css`而不是`custom.scss`。这样，您的网站就可以正确地找到并应用编译后的样式表了。
