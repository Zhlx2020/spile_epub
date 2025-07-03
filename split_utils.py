from bs4 import BeautifulSoup
import zipfile
import tempfile
import os
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

from bs4 import BeautifulSoup

def get_chapter_title(chapter):
    # 优先用EpubHtml的title属性
    if hasattr(chapter, 'title') and chapter.title and chapter.title.strip():
        print(f'[章节标题] 章节 {chapter.file_name}: 使用 chapter.title = "{chapter.title.strip()}"')
        return chapter.title.strip()
    try:
        soup = BeautifulSoup(chapter.content, "html.parser")
        # 优先找 h1.heading-a
        tag = soup.find('h1', class_='heading-a')
        if tag and tag.get_text().strip():
            print(f'[章节标题] 章节 {chapter.file_name}: 匹配 <h1 class="heading-a"> 得到 "{tag.get_text().strip()}"')
            return tag.get_text().strip()
        # 再找 h2.heading-b
        tag = soup.find('h2', class_='heading-b')
        if tag and tag.get_text().strip():
            print(f'[章节标题] 章节 {chapter.file_name}: 匹配 <h2 class="heading-b"> 得到 "{tag.get_text().strip()}"')
            return tag.get_text().strip()
        # 兜底找第一个 h1/h2
        tag = soup.find(['h1', 'h2'])
        if tag and tag.get_text().strip():
            print(f'[章节标题] 章节 {chapter.file_name}: 匹配第一个 <h1>/<h2> 得到 "{tag.get_text().strip()}"')
            return tag.get_text().strip()
        # 兜底找<title>
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            print(f'[章节标题] 章节 {chapter.file_name}: 匹配 <title> 得到 "{title_tag.get_text().strip()}"')
            return title_tag.get_text().strip()
    except Exception as e:
        print(f'[章节标题] 章节 {chapter.file_name}: 解析HTML出错: {e}')
    # 最后兜底用文件名
    print(f'[章节标题] 章节 {chapter.file_name}: 未匹配到标题，使用文件名')
    return chapter.file_name

import re
from ebooklib import epub

import re
from ebooklib import epub

def build_toc_by_number_rule(chapters):
    """
    以整数开头的章节为一级目录，其他（如1.1、前言等）降为二级目录
    """
    toc = []
    current_number_entry = None
    for chapter in chapters:
        title = get_chapter_title(chapter)
        link = chapter.file_name
        chap_id = chapter.id
        link_obj = epub.Link(link, title, chap_id)
        # 只把纯整数开头的（如"1 "或"1."或"2 "）作为一级目录
        if re.match(r'^\d+([\.、\s]|$)', title):
            toc.append((link_obj, []))
            current_number_entry = toc[-1][1]
            print(f'[目录结构] 作为一级目录: "{title}"')
        else:
            if not toc:
                toc.append((epub.Link(link, "正文", chap_id), [link_obj]))
                current_number_entry = toc[-1][1]
                print(f'[目录结构] 未有一级目录，先创建虚拟"正文"')
            else:
                current_number_entry.append(link_obj)
            print(f'[目录结构] 作为二级目录: "{title}"')
    return toc

def add_nav_css_to_book(book, css_path='nav.css'):
    """
    把nav.css文件加入epub，并确保目录页面能引用
    """
    with open(css_path, "rb") as f:
        css_content = f.read()
    nav_css = epub.EpubItem(uid="nav-css", file_name="nav.css", media_type="text/css", content=css_content)
    book.add_item(nav_css)

def patch_nav_ol_inline_style(epub_path):
    """
    给 nav.xhtml 或 toc.xhtml 里的所有 <ol> 标签添加内联样式，去除自动编号
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 解包 epub
        with zipfile.ZipFile(epub_path, "r") as zf:
            zf.extractall(tmpdir)
        # 查找 nav.xhtml 或 toc.xhtml
        nav_path = None
        for root, dirs, files in os.walk(tmpdir):
            for name in files:
                if name.lower() in ("nav.xhtml", "toc.xhtml"):
                    nav_path = os.path.join(root, name)
                    break
            if nav_path:
                break
        if not nav_path:
            print("未找到 nav.xhtml 或 toc.xhtml，跳过目录样式 patch")
            return
        # 用 BeautifulSoup 修改 <ol> 样式
        with open(nav_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "lxml")
        for ol in soup.find_all("ol"):
            style = ol.attrs.get("style", "")
            needed = "list-style: none; margin-left: 0; padding-left: 1em;"
            if needed not in style:
                style = needed + style
            ol.attrs["style"] = style
        with open(nav_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        # 重新打包 epub
        with zipfile.ZipFile(epub_path, "w") as zf:
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, tmpdir)
                    zf.write(full_path, rel_path)