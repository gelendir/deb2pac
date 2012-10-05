import ar
import os
import sys
import tempfile
import tarfile
import logging
logging.basicConfig(level=logging.DEBUG)

from pprint import pformat, pprint

ENCODING = 'utf8'
PKGBUILD_TEMPLATE = "PKGBUILD.tpl"

SIGN_TABLE = {
    '<<': '<',
    '<=': '<=',
    '=' : '=',
    '>=': '>=',
    '>>': '>',
}

def debug(msg):
    logging.debug(pformat(msg))

def file_read(path):
    return open(path, encoding=ENCODING)

def file_write(path):
    return open(path, 'w', encoding=ENCODING)

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

def parse_pkgname(pkgname):

    parsed = []
    packages = pkgname.split(" | ")

    for package in packages:

        if "(" in package and package.endswith(")"):
            package_name, _, version = package.partition(" ")
            version = version.strip("()")
        else:
            package_name, version = (package, None)

        parsed.append((package_name, version))

    return parsed

def parse_relationship(line):

    parsed = []

    pkgnames = line.split(", ")
    for pkgname in pkgnames:

        package = parse_pkgname(pkgname)
        if len(package) > 1:
            parsed.append(package)
        else:
            parsed.append(package[0])

    return parsed

def parse_control_file(control_file):

    pkgconfig = {}
    desc = []

    lines = (x for x in control_file if x.strip())

    for line in lines:
        if line[0] != " ":
            key, sep, value = line.strip().partition(": ")
            pkgconfig[key] = value
        else:
            desc.append(line.strip())

    desc.insert(0, pkgconfig['Description'])
    pkgconfig['Description'] = "\n".join(desc)

    for key in ['Depends', 'Conflicts', 'Provides', 'Replaces']:
        if key in pkgconfig:
            pkgconfig[key] = parse_relationship(pkgconfig[key])

    return pkgconfig

def transform_deb_config(debconfig):

    version, release = debconfig['Version'].split("-")
    short_desc = debconfig['Description'].split("\n")[0]

    dependencies = [x[0] if isinstance(x, list) else x for x in debconfig['Depends']]

    config = {
        'name'          : debconfig['Package'],
        'arch'          : debconfig['Architecture'],
        'url'           : debconfig.get('Homepage', ''),
        'provides'      : debconfig.get('Provides', ''),
        'conflicts'     : debconfig.get('Conflicts', []),
        'replaces'      : debconfig.get('Replaces', []),
        'version'       : version,
        'release'       : release,
        'short_desc'    : short_desc,
        'dependencies'  : dependencies,
    }

    return config

if __name__ == "__main__":

    debpath = sys.argv[1]
    tmpdir = decompress_deb(debpath)
    pprint(tmpdir)

    control_file = os.path.join(tmpdir, "control", "control")
    with open(control_file, encoding=ENCODING) as f:
        metadata = parse_control_file(f)

    pprint(metadata)

    config = transform_deb_config(metadata)
    pprint(config)

