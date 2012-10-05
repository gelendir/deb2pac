pkgname="{name}"
pkgver="{version}"
pkgrel="{release}"
pkgdesc="{short_desc}"
arch=({arch})
url="{url}"
#TODO: find out where license is
license=('unknown')
groups=()
depends=({dependencies})
provides=({provides})
conflicts=({conflicts})
replaces=({replaces})
#TODO: conf files ?
backup=()
options=()
#install=
#changelog=
source=($pkgname-$pkgver.tar.gz)
noextract=()
#md5sums=() #generate with 'makepkg -g'

build() {{
}}

check() {{
}}

package() {{
  cd "$srcdir/$pkgname-$pkgver"
  make DESTDIR="$pkgdir/" install
}}

# vim:set ts=2 sw=2 et:
