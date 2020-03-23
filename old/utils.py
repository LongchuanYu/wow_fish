def myprint(msg):
    import sys
    sys.stdout.write("\r"+str(msg))
    sys.stdout.flush()