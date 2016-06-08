#!/usr/bin/python 
import sys, os, struct, shutil, time
version = "0.2"
#
# nfi Extrac by gutemine is licensed under GPL Version 3
#
line= "------------------------------------------------------------------------"
print line
print "   >>>>>>>>>>>>> nfi Extract by gutemine Version %s <<<<<<<<<<<<<<<" % version
print line
b2m="/sys/module/block2mtd/parameters/block2mtd"

class NfiExtract():
	def __init__(self, nfifile,extractdir):
		#
		# check for swapfile
		# 1GB would help, especially on small boxes when enigma2 is not stopped
		#
		s=open("/proc/meminfo")
		swaps=s.readline()
		while not swaps.startswith("SwapTotal:"):
			swaps=s.readline()
		s.close()
		swapsize=[]
		swapsize=swaps.split()
		if int(swapsize[1]) > 0: 
			print swaps
			print line
		ubifs=False	
		file=open(nfifile,"r")
		header = file.read(32)
		if header[:3] != "NFI":
			print "Sorry, old NFI format deteced"
			file.close()
			return
		else:
			machine_type = header[4:4+header[4:].find("\0")]
			if header[:4] == "NFI3":
				machine_type = "dm7020hdv2"
		print "Dreambox image type: %s" % machine_type
		print line
		# some parameters
		loopdev="/dev/loop8"
		if not os.path.exists(loopdev):
			os.system("mknod /dev/loop8 b 7 8")
		block2mtd_dev="/dev/mtdblock4"
	        deleteoption="%s,remove" % loopdev
		if machine_type == "dm800" or machine_type == "dm500hd" or machine_type == "dm800se":
		        flashsize=128  # we may have images larger then Flash 
		        flashoption="%s,0x4000,0x200" % loopdev
			vidoff=512
			bs=512
			bso=528
		elif machine_type == "dm7020hd":
			flashsize=1024
		        flashoption="%s,0x40000,0x1000" % loopdev
	                vidoff=4096
			bs=4096
			bso=4224
		elif machine_type == "dm8000":
	        	flashsize=512
			flashoption="%s,0x20000,0x800" % loopdev
	                vidoff=512
			bs=2048
			bso=2112
		else: # dm7020hdv2, dm500hdv2, dm800sev2
	        	flashsize=1024
			flashoption="%s,0x20000,0x800" % loopdev
	                vidoff=2048
			bs=2048
			bso=2112
		(total_size, ) = struct.unpack("!L", file.read(4))
		print "Total image size: %s Bytes" % total_size
		print line
		p = 0
		while file.tell() < total_size:
		        (size, ) = struct.unpack("!L", file.read(4))
		        print "Processing partition # %d size %d Bytes" % (p,size)
			output_names = {1: "secondstage.bin", 2: "boot.img", 3: "root.img"}
			if p not in output_names:
				file.seek(size, 1)
				print "Skipping header ..."
			else:
				print "Extracting %s with %d blocksize ..." % (output_names[p],bs)
				output_filename = extractdir + "/" + output_names[p];
				if os.path.exists(output_filename):
					os.remove(output_filename)
				output = open(output_filename, "wb")
				for sector in range(size / bso):
					d = file.read(bso)
					output.write(d[:bs])
				if p > 2:
					# padd root image with zeros to flashsize
					print "Padding to %d MB ..." % flashsize
					blocks=flashsize*1024*1024/bs
					output = open(output_filename, "a")
					z=open("/dev/zero","r")
					empty = z.read(bso)
					z.close()
					while sector < blocks:
						output.write(empty[:bs])
						sector=sector+1
				output.close()
			if p > 1:
				tmpmnt="/tmp/image"
				if not os.path.exists(tmpmnt):
					os.mkdir(tmpmnt)
				else:
					m=open("/proc/mounts")
					mounts=m.read()
					m.close()
					if mounts.find(tmpmnt) is not -1:
						os.system("umount %s" % tmpmnt)
				# delete block2mtd and losetup to have a clean start
				block2mtd=open(b2m,"w")
				block2mtd.write(deleteoption)
				block2mtd.close()
				os.system("losetup -d %s > /dev/null 2>&1" % loopdev)
				# setup loop
				os.system("losetup %s %s" % (loopdev,output_filename))
				# create block2mtd
				block2mtd=open(b2m,"w")
				block2mtd.write(flashoption)
				block2mtd.close()
				if not os.path.exists(block2mtd_dev):
					print "Sorry device %s doesn't exist\n" % block2mtd_dev
				else:
					image=open(output_filename)
					header = image.read(3)
					image.close()
					if header[:3] != "UBI": # jffs2
						print "Mounting jffs2 ..."
						os.system("mount -t jffs2 %s %s" % (block2mtd_dev, tmpmnt))
					else: # ubifs
						ubifs=True
						# live with ubifs is not so easy
						if not os.path.exists("/usr/sbin/ubiattach"):
							print "Sorry, ubiattach not found"
							return
						if not os.path.exists("/usr/sbin/ubidetach"):
							print "Sorry, ubidetach not found"
							return
						u=open("/proc/filesystems")
						fs=u.read()
						u.close()
						if fs.find("ubifs") is -1:
							print "Sorry, ubifs filesystem not available"
						os.system("ubiattach -m 4 -d 1 -O %s" % vidoff)
						# wait a few seconds as ubifs has to initialize
						time.sleep(5)
						if os.path.exists("/dev/ubi1_0"):
							print "Mounting UBIFS ..."
							os.system("mount -t ubifs /dev/ubi1_0 %s" % (tmpmnt))
						else:
							print "Sorry, ubi device is missing"
				m=open("/proc/mounts")
				mounts=m.read()
				m.close()
				if mounts.find(tmpmnt) is not -1:
					print ("Extracting files from %s ..." % output_names[p])
					if p == 2: # boot
						if os.path.exists("%s/boot" % extractdir):
							shutil.rmtree("%s/boot" % extractdir)
						shutil.copytree(tmpmnt, "%s/boot" % extractdir,True)
					else:      # root
						if os.path.exists("%s/image" % extractdir):
							shutil.rmtree("%s/image" % extractdir)
						# don't use shutil as it fails ...
						#shutil.copytree(tmpmnt, "%s/image" % extractdir,True)
						os.system("cp -RP %s %s" % (tmpmnt, extractdir))
						if os.path.exists("%s/image/boot" % extractdir):
							shutil.rmtree("%s/image/boot" % extractdir)
						if os.path.exists("%s/boot" % extractdir):
							shutil.move("%s/boot" % extractdir, "%s/image" % extractdir)
					os.system("umount %s > /dev/null 2>&1" % tmpmnt)
				else:
					print "Sorry, %s could not be mounted"  % output_names[p]
			p=p+1
		if ubifs:
			os.system("ubidetach -m 4 > /dev/null 2>&1")
		# delete block2mtd and losetup on exit
		block2mtd=open(b2m,"w")
		block2mtd.write(deleteoption)
		block2mtd.close()
		os.system("losetup -d %s" % loopdev)
		print line
		print "Extracting %s to %s Finished!" % (nfifile,extractdir)
		print line
#
# check command line Parameters if used as standalone script
#
if len(sys.argv) < 3:
        print "\nUsage: nfi_extract.py imagename.nfi extractdirectory\n"
else:
	nfifile=sys.argv[1]
	extractdir=sys.argv[2]
	if not os.path.exists(nfifile):
		print "Sorry, %s was not found" % nfifile
	else:
		if not os.path.exists(extractdir):
			try:
				os.mkdir(extractdir)
			except:
				pass
		# check if still not existing
		if  not os.path.exists(extractdir):
			print "Sorry, %s is not existing\n" % extractdir
		else:
			if not os.path.isdir(extractdir):
				print "Sorry, %s is not a directory\n" % extractdir
			else:
				if not os.path.exists(b2m):
					print "Sorry this seems to be no OE 2.0 Dreambox image\nas there is no block2mtd in kernel\n"
				else:
					print "Extracting %s to %s" % (nfifile,extractdir)
					print line
					NfiExtract(nfifile,extractdir)
