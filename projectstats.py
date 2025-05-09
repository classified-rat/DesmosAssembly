from glob import glob

if __name__ == "__main__":
    # count lines of python
    total_lineCount: int = 0
    nonempty_lineCount: int = 0
    for file in glob("*.py"):
        with open(file, "r") as FILE:
            lines: list[str] = FILE.readlines()
            total_lineCount += len(lines)
            nonempty_lineCount += len([line for line in lines if not line.strip() == ""])

    print(f"total lines   : {total_lineCount}\n" +
          f"content lines : {nonempty_lineCount}")
