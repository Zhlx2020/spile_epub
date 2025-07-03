# EPUB 分割与合并工具

这是一个基于 Python 的命令行工具，支持**将 EPUB 文件按章节、每 N 章、目录层级或关键词进行分割**，并可**合并多个 EPUB 为一本新书**。分割后的 EPUB 能完整保留原有图片、样式、字体等资源，确保阅读体验与原书一致。

---

## 功能特性

- 支持以下分割方式：
  - 按每章分割
  - 每 N 章分割
  - 按目录层级（TOC）一级标题分割
  - 按标题关键词分割
- 支持多个 EPUB 文件合并为一本新书
- 分割和合并后的 EPUB 均保留原书所有图片、CSS 样式、字体等静态资源
- 支持自定义分割后书名的后缀，可选是否带“第几章”字样
- **目录样式优化**：自动移除分割后 EPUB 目录（nav.xhtml）自动编号，目录更简洁美观
- 兼容大部分主流阅读器和国内外主流电子书格式规范

---

## 安装依赖

```bash
pip install ebooklib beautifulsoup4 lxml
```

> **重要说明**：本工具依赖 `lxml`，以确保目录（nav.xhtml/toc.xhtml）修饰功能稳定无警告。

---

## 目录自动生成规则与自定义方法

分割脚本会自动为每本分割后的 EPUB 生成目录（TOC）。**默认规则如下**：

- **一级目录**：章节标题以纯数字开头（如“1 ”、“2.”、“3、”等）会成为一级目录。
- **二级目录**：其它标题（如“1.1 小节”、“前言”、“附录”等）会作为最近一个一级目录的子目录。
- **特殊情况**：如果开头没有一级目录，会自动创建一个“正文”一级目录，把这些章节放在里面。

**示例效果：**

| 章节标题           | 目录层级   |
| ------------------ | ---------- |
| 1 序章             | 一级目录   |
| 1.1 起步           | 二级目录   |
| 2 发展             | 一级目录   |
| 2.1 深入           | 二级目录   |
| 前言               | 一级目录（若前面没有数字，归为“正文”一级目录下） |
| 附录               | 二级目录或归“正文” |

### 如何自定义目录规则

不同电子书的章节标题格式不尽相同，**你可以根据自己的 epub 修改目录判断规则**。修改方法：

1. **找到并编辑 `build_toc_by_number_rule` 里的正则表达式**，例如：
   ```python
   re.match(r'^\d+([\.、\s]|$)', title)
   ```
   - 如果你的章节标题是“第1章”、“第2卷”，可以改为：
     ```python
     re.match(r'^第\d+', title)
     ```
   - 如果是“Chapter 1”，可以改为：
     ```python
     re.match(r'^(Chapter|CHAPTER)\s*\d+', title, re.I)
     ```

2. **保存脚本，重新运行分割命令**。

### 使用 Sigil 工具可视化检查目录

你可以用 [Sigil](https://sigil-ebook.com/) 查看和调试分割后 EPUB 的目录结构：

1. 下载并安装 Sigil。
2. 用 Sigil 打开分割后的 epub 文件。
3. 在左侧“目录”面板（Table of Contents）检查目录效果。
4. 如目录不理想，回到脚本调整正则，再重新分割测试。

**建议：**先用 Sigil 查看原始 EPUB 章节标题格式，再调整正则，让脚本自动生成理想目录！

---

## 使用方法

### 1. 按每章分割

```bash
python main.py book.epub output_dir --mode chapter
```

### 2. 每 N 章分割

```bash
python main.py book.epub output_dir --mode n_chapters --n 5
```
> `--n` 可自定义每本包含的章节数

### 3. 按目录（TOC）一级标题分割

```bash
python main.py book.epub output_dir --mode toc
```

### 4. 按标题关键词分割（如“卷”、“篇”等）

```bash
python main.py book.epub output_dir --mode keyword --keywords 卷 篇
```
> 可用 `--keywords` 指定任意关键字列表，遇到标题含关键字自动新建一本

### 5. 合并多个 EPUB 文件

```bash
python main.py book1.epub book2.epub book3.epub merged.epub --mode merge
```
> 输出文件 `merged.epub` 即为合并后的新书

---

## 参数说明

- `epub`：待操作的 EPUB 文件（合并模式下可多个）
- `out_dir`：输出目录（分割模式）或输出文件名（合并模式）
- `--mode`：操作模式，支持 `chapter`、`n_chapters`、`toc`、`keyword`、`merge`
- `--n`：每 N 章分割模式下指定每本包含的章节数
- `--keywords`：关键词分割模式下指定关键词列表

---

## 代码结构简要说明

- `main.py`：命令行入口
- `split_by_chapter.py`：按每章分割
- `split_by_n_chapters.py`：每 N 章分割
- `split_by_title_keyword.py`：按关键词分割
- `split_by_toc_level.py`：按目录分割
- `merge_epubs.py`：EPUB 文件合并
- `base_splitter.py`：分割器基类
- `meta_utils.py`：元数据兼容处理工具
- `split_utils.py`：分割与目录样式修饰工具（如 patch_nav_ol_inline_style）

---

## 注意事项 & 实质性建议

- 本工具不会更改原 EPUB 文件，只在指定输出目录或输出文件生成新文件
- 分割与合并后的 EPUB 已自动处理 CSS 链接，确保图片和样式显示正常
- **目录美化提醒**：已内置目录自动编号修饰（patch_nav_ol_inline_style），分割后每本 EPUB 的目录不会再出现多余数字前缀，更加美观简洁；无需手动调整 CSS
- **如遇目录显示异常**（如部分阅读器显示目录仍有编号或目录缺失），请确保已安装 `lxml`，如问题依然存在欢迎反馈
- 如遇极个别电子书结构特殊导致分割后章节不完整，可自定义分割关键字或调整分割方式
- **建议分割大书时优先用目录层级或关键词方式**，避免正文被拆断影响阅读体验
- 支持自定义分割后每本书名格式，方便后续整理与归档
- 若需批量处理大量书籍，可写简单 shell 脚本循环调用本工具

---

## 许可证

MIT License

---

如有建议或问题欢迎提交 issue 或 PR！