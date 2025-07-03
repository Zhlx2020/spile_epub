import os
from ebooklib import epub
from base_splitter import BaseSplitter
from meta_utils import get_meta_value

from bs4 import BeautifulSoup
import ebooklib

def ensure_css_link(chapter_content, css_items):
    soup = BeautifulSoup(chapter_content, "html.parser")
    head = soup.head
    if head is None:
        head = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head)
        else:
            soup.insert(0, head)
    for css in css_items:
        if not soup.find("link", {"href": css.file_name}):
            link_tag = soup.new_tag("link", rel="stylesheet", href=css.file_name, type="text/css")
            head.append(link_tag)
    return str(soup)

class SplitByChapter(BaseSplitter):
    def split(self):
        os.makedirs(self.out_dir, exist_ok=True)
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        for idx, chapter in enumerate(self.chapters):
            new_book = epub.EpubBook()
            title_val = self.book.get_metadata('DC', 'title')
            if title_val:
                main_title = get_meta_value(title_val[0])
            else:
                main_title = "Untitled"
            new_book.set_title(main_title)
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))
            # 确保章节内容引用CSS
            new_content = ensure_css_link(chapter.content, css_items)
            chapter.content = new_content.encode("utf-8")
            new_book.add_item(chapter)
            # 目录
            chap_title = getattr(chapter, 'title', None) or getattr(chapter, 'get_name', lambda: None)() or "无标题"
            new_book.toc = (epub.Link(chapter.file_name, chap_title, chapter.id),)
            self.copy_resources(new_book)
            new_book.spine = ['nav', chapter]
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            filename = os.path.join(self.out_dir, f'chapter_{idx+1}.epub')
            epub.write_epub(filename, new_book)
            print(f"已保存: {filename}")