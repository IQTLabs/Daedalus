#!/usr/bin/env python
import errno
import os
import subprocess
import sys

from fuse import FUSE
from fuse import FuseOSError
from fuse import Operations


class Confused(Operations):

    def __init__(self, root, fakeroot):
        self.root = root
        self.fakeroot = fakeroot

    def _full_path(self, partial, root):
        if partial.startswith('/'):
            partial = partial[1:]
        path = os.path.join(root, partial)
        return path

    def _full_paths(self, partial):
        return (self._full_path(partial, self.root), self._full_path(partial, self.fakeroot))

    def _fake_wrap(self, full_path, fake_path, call_to_fake):
        if os.path.exists(fake_path) and os.path.isfile(fake_path):
            return call_to_fake(fake_path)
        return call_to_fake(full_path)

    def access(self, path, mode):
        full_path, fake_path = self._full_paths(path)

        def _access(p):
            if not os.access(p, mode):
                raise FuseOSError(errno.EACCES)
        return self._fake_wrap(full_path, fake_path, _access)

    def chmod(self, path, mode):
        full_path, fake_path = self._full_paths(path)
        return self._fake_wrap(full_path, fake_path, lambda p: os.chmod(p, mode))

    def chown(self, path, uid, gid):
        full_path, fake_path = self._full_paths(path)
        return self._fake_wrap(full_path, fake_path, lambda p: os.chown(p, uid, gid))

    def getattr(self, path, fh=None):
        full_path, fake_path = self._full_paths(path)
        st = self._fake_wrap(full_path, fake_path, os.lstat)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                        'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path, fake_path = self._full_paths(path)
        dirents = ['.', '..']
        if os.path.isdir(fake_path):
            dirents.extend(os.listdir(fake_path))
        if os.path.isdir(full_path):
            dirents.extend([r for r in os.listdir(
                full_path) if r not in dirents])
        for r in dirents:
            yield r

    def readlink(self, path):
        full_path, _fake_path = self._full_paths(path)
        if full_path.startswith('/'):
            return os.path.relpath(full_path, self.root)
        return full_path

    def mknod(self, path, mode, dev):
        full_path, _ = self._full_paths(path)
        return os.mknod(full_path, mode, dev)

    def rmdir(self, path):
        full_path, _ = self._full_paths(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        full_path, _ = self._full_paths(path)
        return os.mkdir(full_path, mode)

    def statfs(self, path):
        full_path, fake_path = self._full_paths(path)
        stv = self._fake_wrap(full_path, fake_path, os.statvfs)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
                                                         'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
                                                         'f_frsize', 'f_namemax'))

    def unlink(self, path):
        full_path, fake_path = self._full_paths(path)
        return self._fake_wrap(full_path, fake_path, os.unlink)

    def _link(self, name, target, linkf):
        full_path_name, fake_path_name = self._full_paths(name)
        full_path_target, fake_path_target = self._full_paths(target)
        if os.path.exists(fake_path_target) and os.path.isfile(fake_path_target):
            if os.path.exists(full_path_name):
                raise FuseOSError(errno.EACCES)
            return linkf(fake_path_target, fake_path_name)
        return linkf(full_path_target, full_path_name)

    def symlink(self, name, target):
        return self._link(name, target, os.symlink)

    def link(self, name, target):
        return self._link(name, target, os.link)

    def rename(self, old, new):
        full_path_old, fake_path_old = self._full_paths(old)
        full_path_new, fake_path_new = self._full_paths(new)
        if os.path.exists(fake_path_old) and os.path.isfile(fake_path_old):
            return os.rename(fake_path_old, fake_path_new)
        return os.rename(full_path_old, full_path_new)

    def utimens(self, path, times=None):
        full_path, fake_path = self._full_paths(path)
        return self._fake_wrap(full_path, fake_path, lambda p: os.utime(p, times))

    def open(self, path, flags):
        full_path, fake_path = self._full_paths(path)
        return self._fake_wrap(full_path, fake_path, lambda p: os.open(p, flags))

    def create(self, path, mode, fi=None):
        full_path, _ = self._full_paths(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path, fake_path = self._full_paths(path)

        def _truncate_file(p):
            with open(p, 'r+') as f:
                f.truncate(length)
        self._fake_wrap(full_path, fake_path, _truncate_file)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, _fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root, fakeroot, argvs):
    ops = Confused(root, fakeroot)
    if argvs:
        FUSE(ops, mountpoint, nothreads=True, foreground=False)
    else:
        FUSE(ops, mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4:])
