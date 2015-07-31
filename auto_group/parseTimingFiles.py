import sys
import os
import numpy

dirname = sys.argv[1]
filename_out = sys.argv[2]

fout = open(filename_out, 'w')

files = os.listdir(dirname)

list_of_dicts = []
temp_dict = {}
for filename in files:
    print(dirname+filename)
    with open(dirname+filename) as f:
        lines = f.read().splitlines()
    f.close()

    counts = []
    for item in lines:
        counts.append(float(item))
    counts = numpy.array(counts)

    average = numpy.mean(counts)
    stdev = numpy.std(counts)

    fout.write('%s\t%0.16f\t%0.16f\n' % (filename, average, stdev))

fout.close()

