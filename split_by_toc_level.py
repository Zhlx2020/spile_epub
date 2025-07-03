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
        os.makedirs(self.out_dir, exist_ok=True)
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        toc = self.book.toc
        for idx, item in enumerate(toc):
            hrefs = []
            if isinstance(item, epub.Link):
                continue
            if isinstance(item, tuple):
                hrefs.append(item[0].href)
                if len(item) > 1 and isinstance(item[1], list):
                    hrefs += [sub[0].href for sub in item[1] if isinstance(sub, tuple)]
            else:
                hrefs.append(item.href)
            chapters = [ch for ch in self.chapters if ch.file_name in hrefs]
            if not chapters:
                continue
            new_book = epub.EpubBook()
            title_val = self.book.get_metadata('DC', 'title')
            main_title = get_meta_value(title_val[0]) if title_val else "Untitled"
            toc_title = getattr(item[0], 'title', f"Part {idx+1}") if isinstance(item, tuple) else getattr(item, 'title', f"Part {idx+1}")
            new_book.set_title(f"{main_title} - {toc_title}")
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))
            processed_chapters = []
            toc_list = []
            for chapter in chapters:
                new_content = ensure_css_link(chapter.content, css_items)
                chapter.content = new_content.encode("utf-8")
                new_book.add_item(chapter)
                processed_chapters.append(chapter)
                chap_title = get_chapter_title(chapter)
                toc_list.append(epub.Link(chapter.file_name, chap_title, chapter.id))
            new_book.toc = tuple(toc_list)
            self.copy_resources(new_book)
            new_book.spine = ['nav'] + processed_chapters
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            filename = os.path.join(self.out_dir, f'toc_part_{idx+1}.epub')
            epub.write_epub(filename, new_book)
            print(f"已保存: {filename}")