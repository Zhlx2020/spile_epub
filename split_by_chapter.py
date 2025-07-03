import os
from ebooklib import epub
from base_splitter import BaseSplitter
from meta_utils import get_meta_value
from split_utils import ensure_css_link, get_chapter_title, patch_nav_ol_inline_style
import ebooklib

class SplitByChapter(BaseSplitter):
    """
    将每个章节单独拆分为一本EPUB电子书，并处理元数据、目录和样式。
    """
    def split(self):
        # 确保输出目录存在
        os.makedirs(self.out_dir, exist_ok=True)
        # 提取所有CSS样式资源
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        # 遍历每一个章节，单独生成epub
        for idx, chapter in enumerate(self.chapters):
            new_book = epub.EpubBook()
            # 获取主标题
            title_val = self.book.get_metadata('DC', 'title')
            main_title = get_meta_value(title_val[0]) if title_val else "Untitled"
            new_book.set_title(main_title)
            # 设置语言
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            # 设置作者
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))
            # 章节内容处理：确保引用CSS
            new_content = ensure_css_link(chapter.content, css_items)
            chapter.content = new_content.encode("utf-8")
            new_book.add_item(chapter)
            # 目录只包含当前章节
            chap_title = get_chapter_title(chapter)
            new_book.toc = (epub.Link(chapter.file_name, chap_title, chapter.id),)
            # 拷贝资源（图片、字体等）
            self.copy_resources(new_book)
            # 设置阅读顺序
            new_book.spine = ['nav', chapter]
            # 添加NCX和导航页
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            # 生成输出文件名
            filename = os.path.join(self.out_dir, f'chapter_{idx+1}.epub')
            # 写入epub文件
            epub.write_epub(filename, new_book)
            # 修复目录自动编号（去除ol自动编号）
            patch_nav_ol_inline_style(filename)
            print(f"已保存: {filename}")