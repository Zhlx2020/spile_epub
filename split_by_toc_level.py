import os
from ebooklib import epub
from base_splitter import BaseSplitter
from meta_utils import get_meta_value
from split_utils import ensure_css_link, get_chapter_title
import ebooklib


class SplitByTocLevel(BaseSplitter):
    """
    按目录（TOC）一级标题分割，每个一级标题为一本EPUB
    """

    def split(self):
        # 确保输出目录存在
        os.makedirs(self.out_dir, exist_ok=True)
        # 提取原书中的所有样式文件（css）
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        toc = self.book.toc  # 获取原书的目录结构

        # 遍历每个一级目录项，准备分割
        for idx, item in enumerate(toc):
            hrefs = []  # 当前一级目录下所有章节的href集合
            if isinstance(item, epub.Link):
                # 跳过直接是Link的一级目录（通常不会出现）
                continue
            if isinstance(item, tuple):
                # 结构如 (epub.Section, [子章节...])
                hrefs.append(item[0].href)
                # 汇总所有子章节的href
                if len(item) > 1 and isinstance(item[1], list):
                    hrefs += [sub[0].href for sub in item[1] if isinstance(sub, tuple)]
            else:
                # 结构如 epub.Section
                hrefs.append(item.href)
            # 根据hrefs筛选出属于本一级目录的章节
            chapters = [ch for ch in self.chapters if ch.file_name in hrefs]
            if not chapters:
                # 没有匹配到内容则跳过
                continue

            # 创建新EPUB书对象
            new_book = epub.EpubBook()
            # 获取原书主标题
            title_val = self.book.get_metadata('DC', 'title')
            main_title = get_meta_value(title_val[0]) if title_val else "Untitled"
            # 获取当前一级目录标题
            toc_title = getattr(item[0], 'title', f"Part {idx + 1}") if isinstance(item, tuple) else getattr(item,
                                                                                                             'title',
                                                                                                             f"Part {idx + 1}")
            # 设置新书标题为“主标题 - 当前目录标题”
            new_book.set_title(f"{main_title} - {toc_title}")
            # 设置语言
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            # 设置作者
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))

            processed_chapters = []  # 存放处理后的章节
            toc_list = []  # 新书的目录

            # 依次处理每个章节
            for chapter in chapters:
                # 确保章节内容引用了css
                new_content = ensure_css_link(chapter.content, css_items)
                chapter.content = new_content.encode("utf-8")
                new_book.add_item(chapter)
                processed_chapters.append(chapter)
                # 提取章节标题，并加入新目录
                chap_title = get_chapter_title(chapter)
                toc_list.append(epub.Link(chapter.file_name, chap_title, chapter.id))
            # 设置新书目录
            new_book.toc = tuple(toc_list)
            # 复制资源（图片、字体等）
            self.copy_resources(new_book)
            # 设置阅读顺序（spine）
            new_book.spine = ['nav'] + processed_chapters
            # 添加导航和toc
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            # 保存新书
            filename = os.path.join(self.out_dir, f'toc_part_{idx + 1}.epub')
            epub.write_epub(filename, new_book)
            print(f"已保存: {filename}")