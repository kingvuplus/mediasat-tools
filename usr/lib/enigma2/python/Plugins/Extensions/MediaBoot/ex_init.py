import sys, mediaboot
if len(sys.argv) < 3:
    pass
else:
    mediaboot.MediaBootMainEx(sys.argv[1], sys.argv[2], sys.argv[3])