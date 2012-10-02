import os
import sys
import tempfile
import subprocess
import tarfile

def extract_tarfile(filepath, outdir):

    with tarfile.open(filepath) as archive:
        archive.extractall(outdir)

def extract_arfile(filepath, outdir):

    cwd = os.getcwd()

    abspath = os.path.abspath(filepath)
    os.chdir(outdir)

    cmd = ['ar', 'x', abspath]
    subprocess.check_call(cmd)

    os.chdir(cwd)

def decompress_deb(filepath):

    tempdir = tempfile.mkdtemp()
    extract_arfile(filepath, tempdir)

    control_file = os.path.join(tempdir, "control.tar.gz")
    data_file = os.path.join(tempdir, "data.tar.gz")

    for path in ["control", "data"]:
        fullpath = os.path.join(tempdir, path)
        os.mkdir(fullpath)
        tarfile = os.path.join(tempdir, "%s.tar.gz" % path)
        extract_tarfile(tarfile, fullpath)

    return tempdir

def parse_control_file(control_file):

    metadata = {}
    desc = []

    for line in control_file:
        if not line[0] == " ":
            key, sep, value = line.strip().partition(": ")
            metadata[key] = value
        else:
            desc.append(line.strip())

    desc.insert(0, metadata['Description'])
    metadata['Description'] = "\n".join(desc)

    return metadata

if __name__ == "__main__":

    debpath = sys.argv[1]
    tmpdir = decompress_deb(debpath)
    print tmpdir

    control_file = os.path.join(tmpdir, "control", "control")
    with open(control_file) as f:
        metadata = parse_control_file(f)

    print metadata

