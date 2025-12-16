def get_csv_row_count(file_path: str) -> int:
    with open(file_path, mode='r', encoding='utf-8') as f:
        # Subtract 1 for the header row
        return sum(1 for line in f) - 1
