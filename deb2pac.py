import ar
import os
import sys
import tempfile
import tarfile
import logging
logging.basicConfig(level=logging.DEBUG)

from pprint import pformat, pprint

ENCODING = 'utf8'

PKGBUILD_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "PKGBUILD.tpl")

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

def decompress_deb(filepath, outdir):

    extract_arfile(filepath, outdir)

    for archive in ["control", "data"]:
        dirpath = os.path.join(outdir, archive)
        os.mkdir(dirpath)

        filename = "{0}.tar.gz".format(archive)
        tarfile = os.path.join(outdir, filename)
        extract_tarfile(tarfile, dirpath)

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

def convert_pkg_version(package):

    name, version = package

    if version:
        sign, number = version.split(" ")
        name += "%s%s" % (SIGN_TABLE[sign], number)

    return name

def fill_pkgbuild_template(tpl, pkgconfig):

    values = dict(pkgconfig)

    values['arch'] = "'%s'" % values['arch']

    for key in ['dependencies', 'provides', 'conflicts', 'replaces']:
        relations = (convert_pkg_version(x) for x in values[key])
        line = ' '.join("'%s'" % pkg for pkg in relations)
        values[key] = line

    return tpl.format(**values)

def create_pkgbuild(deb_pkgconfig, outdir):

    with file_read(PKGBUILD_TEMPLATE) as f:
        tpl = f.read()

    pkgconfig = transform_deb_config(deb_pkgconfig)
    debug(pkgconfig)

    pkgbuild = fill_pkgbuild_template(tpl, pkgconfig)
    debug(pkgbuild)

    pkgbuild_path = os.path.join(outdir, "PKGBUILD")

    with file_write(pkgbuild_path) as f:
        f.write(pkgbuild)

if __name__ == "__main__":

    tmpdir = tempfile.mkdtemp()
    pprint(tmpdir)

    debpath = sys.argv[1]
    decompress_deb(debpath, tmpdir)

    control_file = os.path.join(tmpdir, "control", "control")
    with open(control_file, encoding=ENCODING) as f:
        metadata = parse_control_file(f)

    pprint(metadata)

    config = transform_deb_config(metadata)
    pprint(config)

    with file_read(PKGBUILD_TEMPLATE) as f:
        tpl = f.read()

    pkgbuild = fill_pkgbuild_template(tpl, config)
    pprint(pkgbuild)

