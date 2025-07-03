import os
import re
from ebooklib import epub
from base_splitter import BaseSplitter
from meta_utils import get_meta_value
from split_utils import ensure_css_link, get_chapter_title, patch_nav_ol_inline_style  # 确保导入目录 patch 工具
import ebooklib

class SplitByTitleKeyword(BaseSplitter):
    """
    按章节标题是否包含指定关键字进行分割。每遇到包含关键字的章节，开启新分册。
    """

    def __init__(self, epub_path, out_dir, keywords):
        super().__init__(epub_path, out_dir)
        # 支持字符串和字符串列表
        self.keywords = keywords if isinstance(keywords, list) else [keywords]

    def split(self):
        # 创建输出目录
        os.makedirs(self.out_dir, exist_ok=True)
        # 收集所有样式文件
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        parts = []            # 最终分册的章节列表
        current_part = []     # 当前分册的章节
        # 遍历所有章节，按标题关键字切分
        for chapter in self.chapters:
            title = get_chapter_title(chapter)
            # 如果标题包含任一关键字，则开启新分册
            if any(re.search(kw, title) for kw in self.keywords):
                if current_part:
                    parts.append(current_part)
                current_part = [chapter]
            else:
                current_part.append(chapter)
        if current_part:
            parts.append(current_part)
        # 为每个分册生成新EPUB
        for idx, part in enumerate(parts):
            new_book = epub.EpubBook()
            # 查找分册命名用的标题（第一个命中关键字的章节）
            titles = [get_chapter_title(ch) for ch in part if any(re.search(kw, get_chapter_title(ch)) for kw in self.keywords)]
            # 提取主书名
            title_val = self.book.get_metadata('DC', 'title')
            main_title = get_meta_value(title_val[0]) if title_val else "Untitled"
            part_title = titles[0] if titles else f"Part {idx+1}"
            new_book.set_title(f"{main_title} - {part_title}")
            # 设置语言
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            # 设置作者
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))
            processed_part = []  # 章节内容
            toc_list = []        # 目录列表
            # 添加分册内所有章节到新书
            for chapter in part:
                # 确保章节内容引用css
                new_content = ensure_css_link(chapter.content, css_items)
                chapter.content = new_content.encode("utf-8")
                new_book.add_item(chapter)
                processed_part.append(chapter)
                # 目录项
                chap_title = get_chapter_title(chapter)
                toc_list.append(epub.Link(chapter.file_name, chap_title, chapter.id))
            # 设置目录
            new_book.toc = tuple(toc_list)
            # 拷贝图片、字体等资源
            self.copy_resources(new_book)
            # 设置阅读顺序
            new_book.spine = ['nav'] + processed_part
            # 添加NCX和目录页
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            # 输出文件名
            filename = os.path.join(self.out_dir, f'keyword_part_{idx+1}.epub')
            # 写入epub文件
            epub.write_epub(filename, new_book)
            # 修复目录编号（去除ol自动编号）
            patch_nav_ol_inline_style(filename)
            print(f"已保存: {filename}")