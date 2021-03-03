# confused
A FUSE based filesystem confuser.

Files under a specified "fake" tree, will appear preferentially in a real tree, via a FUSE mount.

Usage
=====

    pip install -r requirements.txt
    ./confused.py /real/path /mount/point /fake/path

Copy files to /fake/path (or subdirectories thereof). They will appear under /mount/point, overlaying /real/path.
