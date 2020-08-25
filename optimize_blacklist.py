#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from pathlib import Path

import hosts_from_log as utils


# input is two lists of strings: ["ibm", "com"] & ["www", "ibm", "com"]
# checks if the trailing part of domain_to_test, matches top_domain
def is_subdomain(top_domain, domain_to_test):
	top_domain_list = top_domain.split('.')
	test_domain_list = domain_to_test.split('.')
# 	print(f"{top_domain_list} {test_domain_list[-len(top_domain_list):]}, {top_domain_list == test_domain_list[-len(top_domain_list):]}")
	return top_domain_list == test_domain_list[-len(top_domain_list):]
	

blacklist = utils.load_blacklist()

print(f"Got blacklist: {len(blacklist)} entries")



# build a dict with domain depth as key (.com = 1, .co.uk = 2, ibm.com=2 etc)
domain_depth_map = {}
for domain in blacklist:
	components = domain.split('.')
	depth = len(components)
	domains_for_depth = domain_depth_map.get(depth, [])
	domains_for_depth.append(domain)
	domain_depth_map[depth] = domains_for_depth
	


# sort domain_depth_map by ascending depth
domain_depth_map = {k: domain_depth_map[k] for k in sorted(domain_depth_map.keys())}


for k, v in domain_depth_map.items():
	print(f"depth {k} has {len(v)} domains")
	
# for each depth, find/remove any deeper domains covered by a rule at this depth

depths = sorted(domain_depth_map.keys())

# for depth in depths:
# 	print(depth)
# 	domains = domain_depth_map[depth]
# 	for domain in domains:
# 		print("  ", domain)



for i, depth in enumerate(depths[:-2]):
	domains_for_depth = domain_depth_map[depth]
	for top_domain in domains_for_depth:
		for lower_depth in depths[i+1:]:
			lower_domains = domain_depth_map[lower_depth]
			for lower_domain in lower_domains:
				if is_subdomain(top_domain.strip(), lower_domain.strip()):
					lower_domains.remove(lower_domain)
					print(f"{lower_domain} obseleted by {top_domain}")
