# Maintainer: Austin Adams <arch@austinjadams.com>
pkgname=python2-sandvich-git
pkgver=r25
pkgrel=4
pkgdesc="brutally simple document generation"
arch=('any')
url='https://github.com/ausbin/sandvich'
license=('GPL')
depends=('python2')
makedepends=('git')
optdepends=("python2-yaml: for the command-line interface")
provides=('python2-sandvich')
source=("$pkgname::git+https://github.com/ausbin/sandvich.git")
md5sums=('SKIP')

pkgver() {
  cd "$pkgname"
  echo "r$(git rev-list --count HEAD)"
}

package() {
  cd "$srcdir/$pkgname"

  python2 setup.py install --root="$pkgdir/" --optimize=1
  install -Dm 755 bin/sandvich $pkgdir/usr/bin/sandvich
}

# vim:set ts=2 sw=2 et:
