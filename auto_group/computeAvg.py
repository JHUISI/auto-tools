import sys, os


def computeAvg(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    sum = 0
    count = 0
    for i in lines:
        sum += float(i)
        count += 1
    print("Count: ", count)
    print("Sum: ", sum)
    print("<===============>")
    print("Avg: ", sum / count)
    return

if __name__ == "__main__":
    computeAvg(sys.argv[1])
        
    
