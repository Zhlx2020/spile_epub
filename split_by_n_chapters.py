import os
from ebooklib import epub
from base_splitter import BaseSplitter
from meta_utils import get_meta_value
from split_utils import ensure_css_link, get_chapter_title, build_toc_by_number_rule
from split_utils import add_nav_css_to_book, patch_nav_ol_inline_style
import ebooklib

class SplitByNChapters(BaseSplitter):
    def __init__(self, epub_path, out_dir, n_chapters, add_title_suffix=False):
        super().__init__(epub_path, out_dir)
        self.n_chapters = n_chapters
        self.add_title_suffix = add_title_suffix

    def split(self):
        os.makedirs(self.out_dir, exist_ok=True)
        css_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        for i in range(0, len(self.chapters), self.n_chapters):
            new_book = epub.EpubBook()
            title_val = self.book.get_metadata('DC', 'title')
            main_title = get_meta_value(title_val[0]) if title_val else "Untitled"
            subset = self.chapters[i:i+self.n_chapters]
            if self.add_title_suffix:
                start_chapter = i + 1
                end_chapter = i + len(subset)
                new_book.set_title(f"{main_title} - 第{start_chapter}-{end_chapter}章")
            else:
                new_book.set_title(main_title)
            lang_val = self.book.get_metadata('DC', 'language')
            if lang_val:
                new_book.set_language(get_meta_value(lang_val[0]))
            for _, v in self.book.get_metadata('DC', 'creator'):
                new_book.add_author(get_meta_value(v))
            processed_subset = []
            for chapter in subset:
                new_content = ensure_css_link(chapter.content, css_items)
                chapter.content = new_content.encode("utf-8")
                new_book.add_item(chapter)
                processed_subset.append(chapter)
            new_book.toc = build_toc_by_number_rule(processed_subset)
            self.copy_resources(new_book)
            add_nav_css_to_book(new_book)
            new_book.spine = ['nav'] + processed_subset
            new_book.add_item(epub.EpubNcx())
            new_book.add_item(epub.EpubNav())
            filename = os.path.join(self.out_dir, f'chapters_{i+1}_{i+len(subset)}.epub')
            epub.write_epub(filename, new_book)
            patch_nav_ol_inline_style(filename)  # 自动为目录去编号
            print(f"已保存: {filename}")