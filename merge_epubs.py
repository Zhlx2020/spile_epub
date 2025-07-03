import os
from ebooklib import epub
from meta_utils import get_meta_value
import ebooklib
from bs4 import BeautifulSoup

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

def merge_epubs(epub_paths, output_path):
    # 以第一个epub为基础创建新书
    main_book = epub.read_epub(epub_paths[0])
    new_book = epub.EpubBook()
    # 元数据
    title_val = main_book.get_metadata('DC', 'title')
    if title_val:
        main_title = get_meta_value(title_val[0])
    else:
        main_title = "Merged Book"
    new_book.set_title(f"{main_title} (合并 {len(epub_paths)} 本)")

    lang_val = main_book.get_metadata('DC', 'language')
    if lang_val:
        new_book.set_language(get_meta_value(lang_val[0]))
    for _, v in main_book.get_metadata('DC', 'creator'):
        new_book.add_author(get_meta_value(v))

    all_css = []
    all_chapters = []
    resources = []
    # 收集所有章节、样式和资源
    for idx, path in enumerate(epub_paths):
        book = epub.read_epub(path)
        css_items = [item for item in book.get_items() if item.get_type() == ebooklib.ITEM_STYLE]
        for css in css_items:
            # 避免重复文件名
            if css.file_name not in [x.file_name for x in all_css]:
                all_css.append(css)
        # 章节
        for chapter in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            # 加前缀防止不同epub内重名
            prefix = f"book{idx+1}_"
            chapter.id = prefix + chapter.id
            chapter.file_name = prefix + chapter.file_name
            # 确保每章引用所有CSS
            new_content = ensure_css_link(chapter.content, css_items)
            chapter.content = new_content.encode("utf-8")
            all_chapters.append(chapter)
        # 资源
        for item in book.get_items():
            if item.get_type() in [
                ebooklib.ITEM_IMAGE,
                ebooklib.ITEM_STYLE,
                ebooklib.ITEM_FONT,
                ebooklib.ITEM_AUDIO,
                ebooklib.ITEM_VIDEO,
            ]:
                # 防重名
                if item.file_name not in [x.file_name for x in resources]:
                    resources.append(item)
    # 添加资源
    for css in all_css:
        new_book.add_item(css)
    for res in resources:
        new_book.add_item(res)
    # 添加章节
    for chapter in all_chapters:
        new_book.add_item(chapter)
    new_book.spine = ['nav'] + all_chapters
    new_book.add_item(epub.EpubNcx())
    new_book.add_item(epub.EpubNav())
    # 保存
    epub.write_epub(output_path, new_book)
    print(f"已合并输出: {output_path}")