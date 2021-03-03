import random
import os

import numpy
from essential_generators import DocumentGenerator

try:
    os.mkdir('bar')
except OSError:
    pass

gen = DocumentGenerator()
dirs = []
word_list = []
with open('word_list.txt') as f:
    for line in f.readlines():
        index, word = line.strip().split('\t')
        word_list.append(word)
dirs = [word_list[random.randrange(0, len(word_list))] for i in range(1000)]

extensions = {}
count = 0
key = None
with open('extensions.txt', 'r') as f:
     for line in f.readlines():
         if count == 0:
             key = line.strip()
             if key not in extensions:
                 extensions[key] = []
         else:
             if line == '\n':
                 count = -1
             else:
                 extensions[key].append(line.strip())
         count += 1

filenames = []
with open('filenames.txt', 'r') as f:
    for line in f.readlines():
        filenames.append(line.strip())

os.chdir('bar')
cwd = os.getcwd()
kb = 1024

def make_file(extension):
    print(f'extension: {extension}')
    fname = filenames[random.randrange(0, len(filenames))]
    fname = fname.replace('.foo', '.'+extension)
    if extension == 'txt':
        file = open(fname, 'w')
    else:
        file = open(fname, 'wb')
    print(f'writing file: {fname}')
    a = numpy.random.lognormal(3, 1, kb)
    magnitude = 1
    for size in extensions:
        if extension in extensions[size]:
            if '-' in size:
                vals = size.split('-')
                magnitude = int(vals[random.randrange(0,2)])
            else:
                magnitude = int(size)
    maxval = 1
    print(f'magnitude: {magnitude}')
    for i in range(0, magnitude):
        maxval *= int(a[i])
    print(f'maxval: {maxval}')
    if maxval < 2: maxval = 2
    elif maxval > 5000000000: maxval = 5000000000
    size = random.randrange(1, maxval)
    print(f'actual size: {size}')
    if extension == 'txt':
        for i in range(0, size):
            file.write(gen.paragraph())
    else:
        byte_arr = []
        for i in range(0, size):
            byte_arr.append(random.randrange(0, 256))
            if len(byte_arr) == kb*kb*kb:
                file.write(bytearray(byte_arr))
                byte_arr = []
        if len(byte_arr) > 0:
            file.write(bytearray(byte_arr))
    file.close()

def make_dirs(depth=10):
    print(f'directory depth: {depth}')
    if depth == 0:
        os.chdir(cwd)
        return
    b = numpy.random.lognormal(3, 1, kb)
    for i in range(1, random.randrange(2, 4)):
        try:
            dir_name = dirs[random.randrange(0, len(dirs))]
            os.mkdir(dir_name)
            os.chdir(dir_name)
            magnitudes = list(extensions.keys())
            pick_a = extensions[magnitudes[random.randrange(0,len(magnitudes))]]
            pick_b = extensions[magnitudes[random.randrange(0,len(magnitudes))]]
            picks = list(set(pick_a + pick_b))
            print(f'creating {int(b[i])} files...')
            for x in range(0, int(b[i])):
                make_file(picks[random.randrange(0,len(picks))])
            make_dirs(depth=depth-1)
        except OSError:
            pass
    return

make_dirs()
