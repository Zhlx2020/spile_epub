import ebooklib
from ebooklib import epub

class BaseSplitter:
    def __init__(self, epub_path: str, out_dir: str):
        self.epub_path = epub_path
        self.out_dir = out_dir
        self.book = epub.read_epub(epub_path)
        self.chapters = list(self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    def split(self):
        raise NotImplementedError("子类必须实现 split() 方法")

    def copy_resources(self, new_book):
        # 复制所有资源（图片、样式、字体、音视频等，除了文档）
        import ebooklib
        for item in self.book.get_items():
            if item.get_type() in [
                ebooklib.ITEM_IMAGE,
                ebooklib.ITEM_STYLE,
                ebooklib.ITEM_FONT,
                ebooklib.ITEM_AUDIO,
                ebooklib.ITEM_VIDEO,
            ]:
                new_book.add_item(item)