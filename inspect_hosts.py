#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

dodgy = ["ad.", "ads", "adv", "track", "google", "facebook", "fb", "insight",
		 "pixel", "click", "target", "stat", "deal", "tag", "anal",
		 "classifieds"]
		 
to_blacklist = []

with open("hosts", "r+") as f:
	lines = f.readlines()
	f.seek(0)
	for line in lines:
		host = line.strip().split()[1]
		for trigger in sorted(dodgy):
			if trigger in host:
				print(host)
				resp = input("Delete? ").lower()
				if resp == "y":
					lines_to_delete.append(linenum)
					to_blacklist.append(host)
					break
				else:
					f.write(line)

	f.truncate()
	
for host in blacklist:
	print(f"address=/{host}/#")