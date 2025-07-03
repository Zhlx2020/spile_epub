# EPUB Splitting and Merging Tool

A Python command-line tool to **split EPUB files by chapter, every N chapters, TOC level, or title keyword**, and **merge multiple EPUBs into a single new book**. The split EPUBs retain all original images, styles, fonts, and other resources, ensuring the reading experience matches the original.

---
> [简体中文版说明请点这里查看](README.zh.md)
## Features

- Supports the following splitting modes:
  - Split by each chapter
  - Split every N chapters
  - Split by TOC (Table of Contents) top-level headings
  - Split by title keywords
- Supports merging multiple EPUB files into a single new book
- All images, CSS styles, fonts, and static resources are preserved after splitting or merging
- Optionally customize the suffix of the book title for split volumes, including chapter range
- **TOC Style Optimization**: Automatically removes auto-numbering from TOC (nav.xhtml) in split EPUBs for a cleaner look
- Compatible with most mainstream e-readers and EPUB standards

---

## Install Dependencies

```bash
pip install ebooklib beautifulsoup4 lxml
```

> **Note:** This tool requires `lxml` to ensure stable TOC (nav.xhtml/toc.xhtml) patching with no warnings.

---

## TOC Auto-Generation Rules & Customization

When splitting, the script automatically generates a Table of Contents (TOC) for each new EPUB. **Default rules:**

- **Level 1 TOC:** Chapter titles that start with an integer (e.g., "1 ", "2.", "3、") become level 1 TOC entries.
- **Level 2 TOC:** Other titles (e.g., "1.1 Section", "Foreword", "Appendix") are nested as level 2 under the last level 1 entry.
- **Special Case:** If the first chapters do not match level 1, a "Main Content" top-level TOC is created to contain them.

**Example:**

| Chapter Title     | TOC Level   |
| ------------------|------------|
| 1 Introduction    | Level 1    |
| 1.1 Basics        | Level 2    |
| 2 Development     | Level 1    |
| 2.1 Advanced      | Level 2    |
| Foreword          | Level 1 (or in "Main Content" if no previous level 1) |
| Appendix          | Level 2 or in "Main Content" |

### How to Customize TOC Rules

EPUBs from different sources may have different chapter title formats. **You can adjust the TOC rules in the script to match your book.**

1. **Edit the regular expression in `build_toc_by_number_rule`:**
   ```python
   re.match(r'^\d+([\.、\s]|$)', title)
   ```
   - For titles like "Chapter 1" or "CHAPTER 1":
     ```python
     re.match(r'^(Chapter|CHAPTER)\s*\d+', title, re.I)
     ```
   - For titles like "第1章", "第2卷":
     ```python
     re.match(r'^第\d+', title)
     ```

2. **Save the script and rerun the splitting command.**

### Visualize and Test TOC with Sigil

You can use [Sigil](https://sigil-ebook.com/) to check and adjust your EPUB's TOC:

1. Download and install Sigil.
2. Open your split EPUB file in Sigil.
3. Use the "Table of Contents" panel on the left to view how the TOC looks.
4. If it's not ideal, adjust the regex in your script and rerun the split.

**Tip:** Examine your original EPUB’s chapter title format in Sigil before customizing the TOC rule.

---

## Usage

### 1. Split by each chapter

```bash
python main.py book.epub output_dir --mode chapter
```

### 2. Split every N chapters

```bash
python main.py book.epub output_dir --mode n_chapters --n 5
```
> `--n` can be set to any number of chapters per volume

### 3. Split by top-level TOC heading

```bash
python main.py book.epub output_dir --mode toc
```

### 4. Split by title keywords (e.g. "Volume", "Part")

```bash
python main.py book.epub output_dir --mode keyword --keywords Volume Part
```
> Use `--keywords` to specify any set of keywords; a new volume starts whenever a chapter title matches

### 5. Merge multiple EPUB files

```bash
python main.py book1.epub book2.epub book3.epub merged.epub --mode merge
```
> Output file `merged.epub` will contain the merged content

---

## Parameter Reference

- `epub`: The EPUB file(s) to operate on (multiple files for merge mode)
- `out_dir`: Output directory (for split modes) or output filename (for merge)
- `--mode`: Operation mode (`chapter`, `n_chapters`, `toc`, `keyword`, `merge`)
- `--n`: Number of chapters per split (for `n_chapters` mode)
- `--keywords`: Keyword list for splitting (for `keyword` mode)

---

## Code Structure

- `main.py`: CLI entry point
- `split_by_chapter.py`: Split by chapter
- `split_by_n_chapters.py`: Split every N chapters
- `split_by_title_keyword.py`: Split by keyword
- `split_by_toc_level.py`: Split by TOC
- `merge_epubs.py`: Merge EPUB files
- `base_splitter.py`: Base splitter class
- `meta_utils.py`: Metadata compatibility utilities
- `split_utils.py`: Split and TOC patching utilities (e.g. `patch_nav_ol_inline_style`)

---

## Notes & Practical Advice

- The tool does **not** alter original EPUB files; it creates new files in the output directory or as an output file
- All CSS, images, and resource links are auto-patched in split/merged EPUBs to ensure correct display
- **TOC Beautification:** The script auto-removes TOC auto-numbering in each split EPUB, so you get a clean, number-free TOC; no manual CSS fixes needed
- **If you see TOC issues** (e.g. numbering remains or TOC is missing), please ensure `lxml` is installed; if problems persist, please report them
- For rare EPUBs with special structures, customize the TOC regex or splitting strategy as needed
- **Tip:** For large books, splitting by TOC or keywords usually provides the best reading experience
- You can customize how split volumes are named, making organization and archiving easier
- For batch processing, use a shell script or batch file to loop over multiple EPUBs

---

## License

MIT License

---

Suggestions and pull requests are welcome!