#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

dodgy = ["ad.", "ads", "adv", "track", "google", "facebook", "fb", "insight",
		 "pixel", "click", "target", "stat", "deal", "tag", "anal",
		 "classifieds"]
		 
with open(hosts) as f:
	for line in f:
		for trigger in sorted(dodgy):
			if trigger in line:
				print(line)