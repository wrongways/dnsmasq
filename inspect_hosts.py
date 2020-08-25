#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

dodgy = ["ad.", "ads", "adv", "track", "google", "facebook", "fb", "insight",
		 "pixel", "click", "target", "stat", "deal", "tag", "anal",
		 "classifieds"]
		 
allowed = ["static", "googlevideo", "cloudfront.net"]
		 
blacklist = []

with open("hosts", "r+") as f:
	lines = f.readlines()
	f.seek(0)
	for line in lines:
		host = line.strip().split()[1]
		for trigger in sorted(dodgy):
			if trigger in host:
				for ok in allowed:
					if ok in host:
						break
				resp = input(f"Delete {host}? ").lower()
				if resp == "y":
					blacklist.append(host)
					break
				else:
					f.write(line)

	f.truncate()
	
for host in blacklist:
	print(f"address=/{host}/#")