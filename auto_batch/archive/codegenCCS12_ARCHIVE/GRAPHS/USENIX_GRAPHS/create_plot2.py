import os

N = 100
x = 100
xx = 1000
meta  = { 'bbs':None, 'bls':None, 'chp':None, 'chch':None, 'cyh':"ring=20", 'hess':None, 
          'boyen':"ring=3", 'waters05':None, 'waters09':None, 'cl':None, 'chchhess':None, 'vrf':None, 'hw':None }
files = { 'bbs':65, 'boyen':95, 'cl':50, 'vrf':170, 'bls':20, 'hw':25, 'chchhess':45, 'chch':22, 'chp':40, 'cyh':27, 'hess':23, 'waters05':45, 'waters09':120} #'chp':30, 'chch':50, 'cyh':40, 'hess':50, 'bgls':120, 'boyen':150, 'waters05':80 }
# cyh => (ring size = 20)
# boyen => (ring size = 2)

intro = """\n
#!/bin/sh
rm -f *.eps
gnuplot <<EOF
"""

outro = """EOF\n"""

#curve = "MNT224"

config = """
set terminal postscript eps enhanced color 'Helvetica' 10;
set size 0.425,0.425;
set output '%s_MNT_160_codegen.eps';
set yrange [0 : %d]; set xrange[1 : 100]; set xtics autofreq 20;
set title 'MNT160' font 'Helvetica,10';
set xlabel 'Number of signatures';
set ylabel 'ms per signature';
plot '%s' w lines lw 6 title '%s (%s)', \\
 '%s' w lines lw 6 title '%s (%s)'; 
"""

def build_graph( key, y_scale ):
    KEY = key.upper()
    indiv_name = KEY + "_ind.dat"
    if meta[key]: indiv_key = meta[key]
    else: indiv_key = "individual"
    batch_name = KEY + "_bat.dat"
    if meta[key]: batch_key = meta[key] 
    else: batch_key = "batched"    
    return config % (key, y_scale, batch_name, KEY, batch_key, indiv_name, KEY, indiv_key)

def build_config(name):
    output = ""    
    output += intro
    
    for i in files.keys():
        output += "\n"
        output += build_graph(i, files[i])
        output += "\n"
    output += outro + "\n"
        
    for i in files.keys():
        #output += "epstopdf %s_MNT_160_codegen.eps\n" % i
        pass
    
    #print(output)
    f = open(name, 'w')
    f.write(output)
    f.close()
    return

if __name__ == "__main__":
    os.system("rm -f *.eps")
    script = "test_this.sh"
    build_config(script)
    os.system("sh %s" % script)
    os.system("rm -f %s" % script)
