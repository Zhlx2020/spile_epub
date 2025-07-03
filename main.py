import argparse
import sys
from split_by_chapter import SplitByChapter
from split_by_n_chapters import SplitByNChapters
from split_by_toc_level import SplitByTocLevel
from split_by_title_keyword import SplitByTitleKeyword

def main():
    parser = argparse.ArgumentParser(description="EPUB 分割工具")
    parser.add_argument("epub", help="待分割的EPUB文件")
    parser.add_argument("out_dir", help="输出目录")
    parser.add_argument("--mode", choices=["chapter", "n_chapters", "toc", "keyword"], default="chapter", help="分割模式")
    parser.add_argument("--n", type=int, default=5, help="每N章分割（mode=n_chapters时用）")
    parser.add_argument("--keywords", nargs="+", help="标题关键词列表（mode=keyword时用）")
    parser.add_argument("--title-suffix", action="store_true", help="分割后标题带章节区间")
    args = parser.parse_args()
    if args.mode == "chapter":
        SplitByChapter(args.epub, args.out_dir).split()
    elif args.mode == "n_chapters":
        SplitByNChapters(args.epub, args.out_dir, args.n, add_title_suffix=args.title_suffix).split()
    elif args.mode == "toc":
        SplitByTocLevel(args.epub, args.out_dir).split()
    elif args.mode == "keyword":
        if not args.keywords:
            print("缺少 --keywords 参数！")
            sys.exit(1)
        SplitByTitleKeyword(args.epub, args.out_dir, args.keywords).split()

if __name__ == "__main__":
    main()