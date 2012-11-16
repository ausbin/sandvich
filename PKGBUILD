# Maintainer: Austin Adams <screamingmoron@gmail.com>
pkgname=python2-sandvich-git
pkgver=VERSION
pkgrel=1
pkgdesc="brutally simple document generation"
arch=("any")
url="https://github.com/UncleNinja/sandvich"
license=('GPL')
depends=("python2" "python2-yaml")
makedepends=('git')
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
  msg "Starting build..."

  rm -rf "$srcdir/$_gitname-build"
  git clone "$srcdir/$_gitname" "$srcdir/$_gitname-build"
  cd "$srcdir/$_gitname-build"

  # no building to do! :D
}

package() {
  cd "$srcdir/$_gitname-build"

  python2 setup.py install --root="$pkgdir/" --optimize=1
  install -Dm 755 bin/sandvich $pkgdir/usr/bin/sandvich
}

# vim:set ts=2 sw=2 et:
