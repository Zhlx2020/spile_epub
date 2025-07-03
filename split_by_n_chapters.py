import os
from ebooklib import epub
from base_splitter import BaseSplitter
from meta_utils import get_meta_value
from split_utils import ensure_css_link, get_chapter_title, build_toc_by_number_rule
from split_utils import add_nav_css_to_book, patch_nav_ol_inline_style
import ebooklib

class SplitByNChapters(BaseSplitter):
    """
    按每N章分割EPUB，每N章生成一本新书，并自动处理目录和样式。
    """
    def __init__(self, epub_path, out_dir, n_chapters, add_title_suffix=False):
        super().__init__(epub_path, out_dir)
        self.n_chapters = n_chapters  # 每本分册包含的章节数
        self.add_title_suffix = add_title_suffix  # 标题是否加分册章数范围后缀

    def split(self):
        os.makedirs(self.out_dir, exist_ok=True)  # 创建输出目录
        # 收集所有样式项（CSS）
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        # 按n_chapters分组，每组生成一本epub
        for i in range(0, len(self.chapters), self.n_chapters):
            new_book = epub.EpubBook()
            # 获取主标题
            title_val = self.book.get_metadata('DC', 'title')
            main_title = get_meta_value(title_val[0]) if title_val else "Untitled"
            subset = self.chapters[i:i+self.n_chapters]  # 当前分册包含的章节
            # 设置新书标题
            if self.add_title_suffix:
                start_chapter = i + 1
                end_chapter = i + len(subset)
                new_book.set_title(f"{main_title} - 第{start_chapter}-{end_chapter}章")
            else:
                new_book.set_title(main_title)
            # 设置语言
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            # 设置作者
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))
            processed_subset = []
            # 依次处理每章内容
            for chapter in subset:
                # 确保章节内容引用CSS样式
                new_content = ensure_css_link(chapter.content, css_items)
                chapter.content = new_content.encode("utf-8")
                new_book.add_item(chapter)
                processed_subset.append(chapter)
            # 构建分册目录
            new_book.toc = build_toc_by_number_rule(processed_subset)
            # 拷贝图片、字体等资源
            self.copy_resources(new_book)
            # 添加目录专用CSS（如有）
            add_nav_css_to_book(new_book)
            # 设置阅读顺序（spine）
            new_book.spine = ['nav'] + processed_subset
            # 添加NCX和导航
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            # 输出文件名
            filename = os.path.join(self.out_dir, f'chapters_{i+1}_{i+len(subset)}.epub')
            # 写入epub文件
            epub.write_epub(filename, new_book)
            # 修复目录自动编号（去除ol自动编号）
            patch_nav_ol_inline_style(filename)
            print(f"已保存: {filename}")