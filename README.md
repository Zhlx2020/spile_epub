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

---

## 安装依赖

```bash
pip install ebooklib beautifulsoup4
```

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

---

## 注意事项

- 本工具不会更改原 EPUB 文件，只在指定输出目录或输出文件生成新文件
- 分割与合并后的 EPUB 已自动处理 CSS 链接，确保图片和样式显示正常
- 如遇极个别电子书结构特殊导致分割后章节不完整，可自定义分割关键字或调整分割方式

---

## 许可证

MIT License

---

如有建议或问题欢迎提交 issue 或 PR！