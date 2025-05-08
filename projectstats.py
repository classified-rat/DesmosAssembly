from glob import glob

if __name__ == "__main__":
    # count lines of python
    lineCount: int = 0
    for file in glob("*.py"):
        with open(file, "r") as FILE:
            lineCount += len(FILE.readlines())

    print(f"lineCount: {lineCount}")
