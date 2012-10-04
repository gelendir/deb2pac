import ar
import os
import sys
import tempfile
import subprocess
import tarfile
from pprint import pprint

ENCODING = 'utf8'
PKGBUILD_TEMPLATE = "PKGBUILD.tpl"

def extract_tarfile(filepath, outdir):

    with tarfile.open(filepath) as archive:
        archive.extractall(outdir)

def extract_arfile(filepath, outdir):

    ar.extract_archive(filepath, outdir)

def decompress_deb(filepath):

    tempdir = tempfile.mkdtemp()
    extract_arfile(filepath, tempdir)

    for archive in ["control", "data"]:
        fullpath = os.path.join(tempdir, archive)
        os.mkdir(fullpath)

        filename = "{0}.tar.gz".format(archive)
        tarfile = os.path.join(tempdir, filename)
        extract_tarfile(tarfile, fullpath)

    return tempdir

def parse_dependencies(depends):

    packages = []
    parts = depends.split(", ")
    for part in parts:
        if "(" in part and part.endswith(")"):
            package_name, _, version = part.partition(" ")
            version = version.strip("()")
        else:
            package_name, version = (part, None)
        packages.append((package_name, version))

    return packages

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
    metadata['Depends'] = parse_dependencies(metadata['Depends'])

    return metadata

if __name__ == "__main__":

    debpath = sys.argv[1]
    tmpdir = decompress_deb(debpath)
    pprint(tmpdir)

    control_file = os.path.join(tmpdir, "control", "control")
    with open(control_file, encoding=ENCODING) as f:
        metadata = parse_control_file(f)

    pprint(metadata)

