# This is an example PKGBUILD file. Use this as a start to creating your own,
# and remove these comments. For more information, see 'man PKGBUILD'.
# NOTE: Please fill out the license field for your package! If it is unknown,
# then please put 'unknown'.

# Maintainer: Your Name <youremail@domain.com>
pkgname={name}
pkgver={version}
pkgrel={release}
epoch=
pkgdesc="{short_desc}"
arch=({arch})
url="{homepage}"
#TODO: find out where license is
license=('GPL')
groups=()
depends=({dependencies})
makedepends=()
checkdepends=()
optdepends=()
provides=({provides})
conflicts=({conflicts})
replaces=({replaces})
backup=()
options=()
install=
changelog=
source=($pkgname-$pkgver.tar.gz)
noextract=()
md5sums=() #generate with 'makepkg -g'

build() {
  cd "$srcdir/$pkgname-$pkgver"
  ./configure --prefix=/usr
  make
}

check() {
  cd "$srcdir/$pkgname-$pkgver"
  make -k check
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  make DESTDIR="$pkgdir/" install
}

# vim:set ts=2 sw=2 et:
