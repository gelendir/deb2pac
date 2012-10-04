import os
from pprint import pprint

MAGIC_STR = "!<arch>\n"
MAGIC_LEN = len(MAGIC_STR)

def extract_file_header(f):

    header = {
        'name'          : f.read(16).strip().decode('utf8'),
        'timestamp'     : int(f.read(12).strip()),
        'owner_id'      : int(f.read(6).strip()),
        'group_id'      : int(f.read(6).strip()),
        'file_mode'     : int(f.read(8).strip()),
        'size'          : int(f.read(10).strip()),
        'file_magic'    : f.read(2).decode('ascii'),
    }

    if header['file_magic'] != "\x60\x0a":
        raise Exception("invalid file magic %s" % header['file_magic'])

    return header

def extract_file(archive, header, outdir):

    path = os.path.join(outdir, header['name'])

    with open(path, 'wb') as f:
        data = archive.read(header['size'])
        f.write(data)

def extract_archive(filepath, outdir):

    filesize = os.path.getsize(filepath)

    with open(filepath, 'rb') as f:

        magic = f.read(MAGIC_LEN).decode('utf8')
        if magic != MAGIC_STR:
            raise Exception("%s does not seem to be a valid ar archive" % filepath)

        while f.tell() < filesize:
            header = extract_file_header(f)
            extract_file(f, header, outdir)

            if header['size'] % 2 == 1:
                f.read(1)

if __name__ == "__main__":
    import sys
    filepath = sys.argv[1]
    extract_archive(filepath, ".")
