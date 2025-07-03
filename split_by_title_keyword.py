import os
import re
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

class SplitByTitleKeyword(BaseSplitter):
    def __init__(self, epub_path, out_dir, keywords):
        super().__init__(epub_path, out_dir)
        self.keywords = keywords if isinstance(keywords, list) else [keywords]

    def split(self):
        os.makedirs(self.out_dir, exist_ok=True)
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        parts = []
        current_part = []
        for chapter in self.chapters:
            title = chapter.get_name() or ""
            if any(re.search(kw, title) for kw in self.keywords):
                if current_part:
                    parts.append(current_part)
                current_part = [chapter]
            else:
                current_part.append(chapter)
        if current_part:
            parts.append(current_part)
        for idx, part in enumerate(parts):
            new_book = epub.EpubBook()
            titles = [ch.get_name() for ch in part if any(re.search(kw, ch.get_name() or "") for kw in self.keywords)]
            title_val = self.book.get_metadata('DC', 'title')
            if title_val:
                main_title = get_meta_value(title_val[0])
            else:
                main_title = "Untitled"
            part_title = titles[0] if titles else f"Part {idx+1}"
            new_book.set_title(f"{main_title} - {part_title}")
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))
            processed_part = []
            toc_list = []
            for chapter in part:
                new_content = ensure_css_link(chapter.content, css_items)
                chapter.content = new_content.encode("utf-8")
                new_book.add_item(chapter)
                processed_part.append(chapter)
                chap_title = getattr(chapter, 'title', None) or getattr(chapter, 'get_name', lambda: None)() or "无标题"
                toc_list.append(epub.Link(chapter.file_name, chap_title, chapter.id))
            new_book.toc = tuple(toc_list)
            self.copy_resources(new_book)
            new_book.spine = ['nav'] + processed_part
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            filename = os.path.join(self.out_dir, f'keyword_part_{idx+1}.epub')
            epub.write_epub(filename, new_book)
            print(f"已保存: {filename}")