import argparse
import sys
from split_by_chapter import SplitByChapter
from split_by_n_chapters import SplitByNChapters
from split_by_toc_level import SplitByTocLevel
from split_by_title_keyword import SplitByTitleKeyword
from merge_epubs import merge_epubs   # <--- 新增

def main():
    parser = argparse.ArgumentParser(description="EPUB 批量分割/合并工具")
    parser.add_argument("epub", nargs="+", help="待分割或者合并的EPUB文件（合并时可多个）")
    parser.add_argument("out_dir", help="输出目录或合并输出文件")
    parser.add_argument("--mode", choices=["chapter", "n_chapters", "toc", "keyword", "merge"], default="chapter", help="操作模式")
    parser.add_argument("--n", type=int, default=5, help="每N章分割（mode=n_chapters时用）")
    parser.add_argument("--keywords", nargs="+", help="标题关键词列表（mode=keyword时用）")
    args = parser.parse_args()
    if args.mode == "merge":
        # 合并模式
        output_path = args.out_dir
        merge_epubs(args.epub, output_path)
    else:
        epub_path = args.epub[0]
        if args.mode == "chapter":
            SplitByChapter(epub_path, args.out_dir).split()
        elif args.mode == "n_chapters":
            SplitByNChapters(epub_path, args.out_dir, args.n).split()
        elif args.mode == "toc":
            SplitByTocLevel(epub_path, args.out_dir).split()
        elif args.mode == "keyword":
            if not args.keywords:
                print("缺少 --keywords 参数！")
                sys.exit(1)
            SplitByTitleKeyword(epub_path, args.out_dir, args.keywords).split()

if __name__ == "__main__":
    main()