import sys

for line in sys.stdin:
    print(line.decode("gb18030").encode("utf-8").strip())
