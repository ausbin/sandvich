# Maintainer: Austin Adams <screamingmoron@gmail.com>
pkgname=python2-sandvich-git
pkgver=VERSION
pkgrel=3
pkgdesc="brutally simple document generation"
arch=("any")
url="https://github.com/UncleNinja/sandvich"
license=('GPL')
depends=("python2")
makedepends=('git')
optdepends=("python2-yaml: for the command-line interface")
provides=("python2-sandvich")
options=(!emptydirs)

_gitroot=git://github.com/UncleNinja/sandvich.git
_gitname=sandvich

build() {
  cd "$srcdir"
  msg "Connecting to GIT server...."

  if [[ -d "$_gitname" ]]; then
    cd "$_gitname" && git pull origin
    msg "The local files are updated."
  else
    git clone "$_gitroot" "$_gitname"
  fi

  msg "GIT checkout done or server timeout"
}

package() {
  cd "$srcdir/$_gitname"

  python2 setup.py install --root="$pkgdir/" --optimize=1
  install -Dm 755 bin/sandvich $pkgdir/usr/bin/sandvich
}

# vim:set ts=2 sw=2 et:
