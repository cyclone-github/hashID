#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @name: hashID.py
# @author: c0re <https://psypanda.org/>                           
# @date: 2014/03/07
# @copyright: <https://www.gnu.org/licenses/gpl-3.0.html>

import re, os, sys, argparse

#set essential variables
version = "v2.3.0"
banner = "%(prog)s " + version + " by c0re <https://github.com/psypanda/hashID>\nLicense GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>"
usage = "%(prog)s (-i HASH | -f FILE) [-o OUTFILE] [--help] [--version]"
description = "identify the different types of hashes"

#configure argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, usage=usage, description=description)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-i", "--identify", type=str, help="identify a single hash")
group.add_argument("-f", "--file", type=argparse.FileType("r"), help="analyse a given file")
parser.add_argument("-o", "--output", type=str, default="hashid_output.txt", help="sets a different output filename (default: %(default)s)")
#parser.add_argument("-n", "--notfound", action='store_true', help="create a separate file containing all unknown hashes")
parser.add_argument("--version", action="version", version=banner)
args = parser.parse_args()

#identify the input hash
def identifyHash(phash):
	#trim possible whitespace
	phash = phash.strip()
	#set regex and algorithms
	prototypes = \
	(
		("^[a-f0-9]{4}$", ("CRC-16","CRC-16-CCITT","FCS-16")),
		("^[a-f0-9]{8}$", ("Adler-32","CRC-32","CRC-32B","FCS-32","GHash-32-3","GHash-32-5","FNV-132","Fletcher-32","Joaat","ELF-32","XOR-32")),
		("^\+[a-z0-9\/\.]{12}$", ("Blowfish(Eggdrop)",)),
		("^[a-z0-9\/\.]{13}$", ("DES(Unix)","Traditional DES","DEScrypt")),
		("^[a-f0-9]{16}$", ("MySQL323","DES(Oracle)","VNC","Half MD5","Oracle 7-10g","FNV-164","CRC-64")),
		("^[a-z0-9\/\.]{16}$", ("Cisco-PIX(MD5)",)),
		("^\([a-z0-9\+\/]{20}\)$", ("Lotus Domino",)),
		("^_[a-z0-9\/\.]{19}$", ("BSDi Crypt",)),
		("^[a-f0-9]{24}$", ("CRC-96(ZIP)",)),
		("^[a-z0-9\/\.]{24}$", ("Crypt16",)),
		("^[0-9a-f]{32}$", ("MD5","NTLM","LM","MD4","MD2","RAdmin v2.x","RIPEMD-128","Haval-128","Tiger-128","Snefru-128","MD5(ZipMonster)","Skein-256(128)","Skein-512(128)")),
		("^{SHA}[a-z0-9\/\+]{27}=$", ("SHA-1(Base64)","Netscape LDAP SHA")),
		("^\$1\$[a-z0-9\/\.]{0,8}\$[a-z0-9\/\.]{22}$", ("MD5(Unix)","Cisco-IOS(MD5)","FreeBSD MD5")),
		("^0x[a-f0-9]{32}$", ("Lineage II C4",)), 
		("^\$H\$[a-z0-9\/\.]{31}$", ("MD5(phpBB3)",)),
		("^\$P\$[a-z0-9\/\.]{31}$", ("MD5(Wordpress)","PHPass' Portable Hash")),
		("^[a-f0-9]{32}:[a-z0-9]{2}$", ("osCommerce","xt:Commerce")),
		("^\$apr1\$.{0,8}\$[a-z0-9\/\.]{22}$", ("MD5(APR)","Apache MD5")),
		("^{smd5}.{31}$", ("AIX(smd5)",)),
		("^[a-f0-9]{32}:[0-9]{4}$", ("WebEdition CMS",)),
		("^[a-f0-9]{32}:.{5}$", ("IP.Board v2+","MyBB v1.2+")),
		("^[a-z0-9]{34}$", ("CryptoCurrency(Adress)",)),
		("^[a-f0-9]{40}$", ("SHA-1","RIPEMD-160","Haval-160","SHA-1(MaNGOS)","SHA-1(MaNGOS2)","Tiger-160","HAS-160","Skein-256(160)","Skein-512(160)")),
		("^\*[a-f0-9]{40}$", ("MySQL5.x","MySQL4.1")),
		("^[a-z0-9]{43}$", ("Cisco-IOS(SHA256)",)),
		("^[a-f-0-9]{32}:[^\\\/:*?\"\<\>\|]{1,15}$", ("Domain Cached Credentials 2",)),
		("^{SSHA}[a-z0-9\+\/]{38}={0,2}$", ("SSHA-1(Base64)","Netscape LDAP SSHA")),
		("^[a-z0-9]{47}$", ("FortiOS",)),
		("^[a-f0-9]{48}$", ("Haval-192","Tiger-192","OSX v10.4","OSX v10.5","OSX v10.6")),
		("^[a-f0-9]{51}$", ("Palshop CMS",)),
		("^[a-z0-9]{51}$", ("CryptoCurrency(PrivateKey)",)),
		("^{ssha1}[a-z0-9\.\$]{47}$", ("AIX(ssha1)",)),
		("^0x0100[a-f0-9]{48}$", ("MSSQL(2005)","MSSQL(2008)")),
		("^\$md5,rounds=[0-9]+\$[a-z0-9\.\/]{0,8}(\$|\$\$)[a-z0-9\.\/]{22}$", ("MD5(Sun)",)),
		("^[a-f0-9]{56}$", ("SHA-224","Haval-224","Keccak-224","Skein-256(224)","Skein-512(224)")),
		("^(\$2a|\$2y|\$2)\$[0-9]{0,2}?\$[a-z0-9\/\.]{53}$", ("Blowfish(OpenBSD)",)),
		("^S:[a-f0-9]{60}$", ("Oracle 11g",)),
		("^\$bcrypt-sha256\$.{5}\$[a-z0-9\/\.]{22}\$[a-z0-9\/\.]{31}$", ("BCrypt(SHA256)",)),
		("^[a-f0-9]{32}:[a-z0-9]{30}$", ("vBulletin >v3.8.5",)),
		("^[a-f0-9]{64}$", ("SHA-256","RIPEMD-256","Haval-256","Snefru-256","GOST R 34.11-94","Keccak-256","Skein-256","Skein-512(256)")),
		("^[a-f0-9]{32}:[a-z0-9]{32}$", ("Joomla",)),
		("^[a-f-0-9]{32}:[a-f-0-9]{32}$", ("SAM(LM_Hash:NT_Hash)",)),
		("^\$episerver\$\*0\*[a-z0-9=\*+]{52}$", ("EPiServer 6.x <v4",)),
		("^{ssha256}[a-z0-9\.\$]{63}$", ("AIX(ssha256)",)),
		("^[a-f0-9]{80}$", ("RIPEMD-320",)),
		("^\$episerver\$\*1\*[a-z0-9=\*+]{68}$", ("EPiServer 6.x >v4",)),
		("^0x0100[a-f0-9]{88}$", ("MSSQL(2000)",)),
		("^[a-f0-9]{96}$", ("SHA-384","Keccak-384","Skein-512(384)","Skein-1024(384)")),
		("^{SSHA512}[a-z0-9\+\/]{96}={0,2}$", ("SSHA-512(Base64)","LDAP(SSHA512)")),
		("^{ssha512}[a-z0-9\.\$]{107}$", ("AIX(ssha512)",)),
		("^[a-f0-9]{128}$", ("SHA-512","Whirlpool","Salsa10","Salsa20","Keccak-512","Skein-512","Skein-1024(512)")),
		("^[a-f0-9]{136}$", ("OSX v10.7",)),
		("^0x0200[a-f0-9]{136}$", ("MSSQL(2012)",)),
		("^\$ml\$.+$", ("OSX v10.8",)),
		("^[a-f0-9]{256}$", ("Skein-1024",)),
		("^grub\.pbkdf2\.sha512\..+$", ("GRUB 2",)),
		("^sha1\$[a-z0-9\/\.]{1,12}\$[a-f0-9]{40}$", ("SHA-1(Django)",)),
		("^\$S\$[a-z0-9\/\.]{52}$", ("SHA-512(Drupal)",)),
		("^\$5\$.{0,22}\$[a-z0-9\/\.]{43,69}$", ("SHA-256(Unix)",)),
		("^\$6\$.{0,22}\$[a-z0-9\/\.]{86}$", ("SHA-512(Unix)",)),
		("^\$sha\$[a-z0-9]{1,16}\$[a-f0-9]{64}$", ("Minecraft(AuthMe Reloaded)",)),
		("^sha256\$[a-z0-9\/\.]{1,12}\$[a-f0-9]{64}$", ("SHA-256(Django)",)),
		("^sha384\$[a-z0-9\/\.]{1,12}\$[a-f0-9]{96}$", ("SHA-384(Django)",)),
		("^[^\\\/:*?\"\<\>\|]{1,15}:[^\\\/:*?\"\<\>\|]{1,15}:[a-f0-9]{32}:[a-f0-9]{32}:{0,3}$", ("Domain Cached Credentials",)),
		("^\$scram\$.+$", ("SCRAM Hash",))
	)
	for hashtype in prototypes:
		#try to find matches
		if (re.match(hashtype[0], phash, re.IGNORECASE)):
			for h in hashtype[1]:
				yield h


#analyse a given file
def analyseFile(infile, outfile):
	#define the counters
	hashesAnalysed = 0
	hashesFound = 0
	#show input file path
	print ("Analysing '" + os.path.abspath(infile.name) + "'")
	for line in infile:
		#increment hash count
		hashesAnalysed += 1
		#trim possible whitespace
		line = line.strip()
		#try to identify the hash
		identify = identifyHash(line)
		outfile.write("Analysing '" + line + "'\n")
		hashesFound += showResult(identify, outfile)
		#add a newline
		outfile.write("\n")
	#show number of hashes analysed
	print ("Hashes analysed: " + str(hashesAnalysed))
	#show number of hashes found
	print ("Hashes found: " + str(hashesFound))
	#show output file path
	print ("Output written: '" + os.path.abspath(outfile.name) + "'")


#create human readable output
def showResult(identify, outfile):
	#define the counter
	count = 0
	#iterate over matches
	for result in identify:
		if count == 0:
			outfile.write("Most possible:\n")
		elif count == 2:
			outfile.write("Less possible:\n")	
		#write the result
		outfile.write("[+] " + result + "\n")
		#increment counter
		count += 1
	#check for unknown hash
	if count == 0:
		outfile.write("[+] Unknown hash\n")
	return (count > 0)


#analyse a single hash
if args.identify:
	print ("Analysing '" + args.identify + "'")
	showResult(identifyHash(args.identify), sys.stdout)
#analyse a file
elif args.file:
	outfile = open(args.output, "w")
	analyseFile(args.file, outfile)
	outfile.close()