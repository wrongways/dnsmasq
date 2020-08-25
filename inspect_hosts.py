#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

# Copyright © Jez Wain 2020



dodgy = ["ad.", "ads", "adv", "track", "google", "facebook", "fb", "insight",
		 "pixel", "click", "target", "stat", "deal", "tag", "anal",
		 "classifieds"]
		 
whitelist = ["static", "googlevideo", "cloudfront.net", "adventures", "adjust",
			 "state", "upload", "download", "roads", "reads", "youtube", "ytimg", "ajax",
			 "googleapis", "loopinsight", "advance", "leads", "spotify", "typepad",
			 "advisor", "cloudflare.net", "bluemix", "advocate", "stage", "instagram"]
		 
blacklist = []

def is_dodgy(host):
	for trigger in whitelist:
		if trigger in host:
			return False
		
	for trigger in dodgy:
		if trigger in host:
			return True
	
	return False


with open("hosts", "r+") as f:
	lines = f.readlines()
	f.seek(0)
	for line in lines:
		host = line.strip().split()[1]
		if is_dodgy(host):
			resp = input(f"Delete {host}? ").lower()
			if resp == "y":
				blacklist.append(host)
				continue
		
		f.write(line)

	f.truncate()
	
for host in blacklist:
	print(f"address=/{host}/#")