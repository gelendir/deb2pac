import sys
from pprint import pprint

MAGIC_STR = "!<arch>\n"
MAGIC_LEN = len(MAGIC_STR)

def extract_file_header(f):

    sizes = [
        ('name', 16),
        ('timestamp', 12),
        ('owner_id', 6),
        ('group_id', 6),
        ('file_mode', 8),
        ('file_size', 10),
        ('file_magic', 2),
    ]

    header = dict( (key, f.read(size)) for (key, size) in sizes )

    return header

if __name__ == "__main__":

    with open(sys.argv[1], 'rb') as f:
        f.read(MAGIC_LEN)
        pprint(extract_file_header(f))

