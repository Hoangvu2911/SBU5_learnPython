import argparse
import re
import sys
from typing import List

class LogAnalyzer:
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logs = self._read_logs()

    def _read_logs(self) -> List[str]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file '{self.file_path}'")
            sys.exit(1)

    def filter_by_level(self, level: str) -> List[str]:
        pattern = re.compile(rf"\[{level.upper()}\]")
        
        return [line for line in self.logs if pattern.search(line)]

    def search_keyword(self, logs: List[str], keyword: str) -> List[str]:
        match_condition = lambda line: keyword.lower() in line.lower()
        
        return list(filter(match_condition, logs))

    def analyze(self, level: str = None, keyword: str = None):
        result_logs = self.logs

        if level:
            result_logs = self.filter_by_level(level)

        if keyword:
            result_logs = self.search_keyword(result_logs, keyword)

        self._display_results(result_logs)

    def _display_results(self, results: List[str]):
        print(f"\n--- KẾT QUẢ PHÂN TÍCH ({len(results)} dòng) ---")
        for line in results:
            print(line.strip())
        print("-" * 40 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="CLI Log Analyzer - Công cụ phân tích log đơn giản.",
        epilog="Ví dụ: python demo_cli.py server.log -l ERROR -k 'timeout'"
    )

    parser.add_argument(
        "file",
        type=str,
        help="Đường dẫn tới file log cần phân tích (VD: server.log)"
    )
    
    parser.add_argument(
        "-l", "--level",
        type=str,
        choices=["INFO", "ERROR", "WARNING", "DEBUG"],
        help="Lọc log theo cấp độ"
    )
    
    parser.add_argument(
        "-k", "--keyword",
        type=str,
        help="Tìm kiếm từ khóa cụ thể trong nội dung log"
    )

    args = parser.parse_args()

    analyzer = LogAnalyzer(args.file)
    analyzer.analyze(level=args.level, keyword=args.keyword)


if __name__ == "__main__":
    main()