import os

N = 100

SS512ones = ["DSE", "BGW", "DFA"]

files = {'BSW':2000, 'LW':2000}

intro = """\n
#!/bin/sh
rm -f *.pdf *.eps
gnuplot <<EOF
"""

outro = """EOF\n"""

#curve = "MNT224"

config_MNT_160 = """
set terminal postscript eps enhanced color 'Helvetica' 10;
set size 0.425,0.425;
set output '%s_MNT_160_CloudSource.eps';
set yrange [0 : %d]; set xrange[1 : 100]; set xtics autofreq 20;
set title 'MNT160 Threshold Estimator' font 'Helvetica,10';
set xlabel 'Number of attributes in access-control policy';
set ylabel 'Encryption time (ms)';
plot '%s' w lines lw 6 title '%s';
"""

config_SS_512 = """
set terminal postscript eps enhanced color 'Helvetica' 10;
set size 0.425,0.425;
set output '%s_SS_512_CloudSource.eps';
set yrange [0 : %d]; set xrange[1 : 100]; set xtics autofreq 20;
set title 'SS512 Threshold Estimator' font 'Helvetica,10';
set xlabel 'Number of attributes in access-control policy';
set ylabel 'Encryption time (ms)';
plot '%s' w lines lw 6 title '%s';
"""

def build_graph( key, y_scale ):
    KEY = key.upper()
    file_name = "Test" + key + "_decrypt.dat"
    if (key in SS512ones):
        return config_SS_512 % (key, y_scale, file_name, KEY)
    else:
        return config_MNT_160 % (key, y_scale, file_name, KEY)

def build_config(name):
    output = ""    
    output += intro
    
    for i in files.keys():
        output += "\n"
        output += build_graph(i, files[i])
        output += "\n"
    output += outro + "\n"

    
    for i in files.keys():
        if (i in SS512ones):
            output += "epstopdf %s_SS_512_CloudSource.eps\n" % i
        else:
            output += "epstopdf %s_MNT_160_CloudSource.eps\n" % i

    
    print(output)
    f = open(name, 'w')
    f.write(output)
    f.close()
    return

if __name__ == "__main__":
    #os.system("rm -f *.eps *.pdf")
    script = "test_this.sh"
    build_config(script)
    os.system("sh %s" % script)
    os.system("rm -f %s" % script)
