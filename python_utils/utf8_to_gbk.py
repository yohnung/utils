import sys

for line in sys.stdin:
    print(line.decode("utf-8").encode("gb18030").strip())
