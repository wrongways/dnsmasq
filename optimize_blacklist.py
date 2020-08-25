#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from pathlib import Path


def load_blacklist():
	blacklisted_domains = {}
	cwd = Path('.')
	for conffile in cwd.glob('*.conf'):
		linenum = 0
		with open(conffile) as f:
			for line in f:
				if line.startswith('address'):
					domain = line.split("/")[1]
					domain = domain.lower()
					file_refs = blacklisted_domains.get(domain, [])
					file_refs.append((conffile, linenum))
					blacklisted_domains[domain] = file_refs
					
				linenum += 1

	return blacklisted_domains
	
	
def is_blacklisted(domain, blacklist):
	for black_domain in blacklist:
		if is_subdomain(black_domain, domain):
			return True
			
	return False


# input is two lists of strings: "ibm.com" & "www.ibm.com"
# checks if the trailing part of domain_to_test, matches top_domain
def is_subdomain(top_domain, domain_to_test):
	top_domain_list = top_domain.split('.')
	test_domain_list = domain_to_test.split('.')
# 	print(f"{top_domain_list} {test_domain_list[-len(top_domain_list):]}, {top_domain_list == test_domain_list[-len(top_domain_list):]}")
	return top_domain_list == test_domain_list[-len(top_domain_list):]
	

def domains_by_depth(blacklist):
# build a dict with domain depth as key (.com = 1, .co.uk = 2, ibm.com=2 etc)
	domain_depth_map = {}
	for domain in blacklist:
		components = domain.split('.')
		depth = len(components)
		domains_for_depth = domain_depth_map.get(depth, [])
		domains_for_depth.append(domain)
		domain_depth_map[depth] = domains_for_depth

	# sort domain_depth_map by ascending depth
	return {k: domain_depth_map[k] for k in sorted(domain_depth_map.keys())}


def check_for_duplicates(blacklist, verbose=True):
	if verbose:
		print("Checking for blacklist duplicates...")
	
	for domain, file_refs in blacklist.items():
		if len(file_refs) > 1:
			print(domain)
			for (file_path, linenum) in file_refs:
				print("  ", file_path.name, linenum)
				
				
# for each depth, find/remove any deeper domains covered by a rule at this depth
def check_for_overlaps(blacklist, remove=False, verbose=True):

	if verbose:
		print("Checking blacklist for overlaps...")
	domain_depth_map = domains_by_depth(blacklist)
	depths = sorted(domain_depth_map.keys())
	for i, depth in enumerate(depths[:-2]):
		domains_for_depth = domain_depth_map[depth]
		for top_domain in domains_for_depth:
			for lower_depth in depths[i+1:]:
				lower_domains = domain_depth_map[lower_depth]
				for lower_domain in lower_domains:
					if is_subdomain(top_domain.strip(), lower_domain.strip()):
						(lower_file_path, lower_linenum) = blacklist[lower_domain][0]
						(upper_file_path, upper_linenum) = blacklist[top_domain][0]
						print(f"{lower_domain}"
							  f" ({lower_file_path.name}, line {lower_linenum:,})"
							  f" obseleted by {top_domain}"
							  f" ({upper_file_path.name}, line {upper_linenum:,})")
						
						if remove:
							lower_domains.remove(lower_domain)


	

def print_depthmap_info(domain_depth_map, verbose=False):
	print(f"Blacklist with {len(blacklist)} entries")
	for k, v in domain_depth_map.items():
		print(f"depth {k} has {len(v)} domains")

	if verbose:
		for depth in domain_depth_map:
			print(depth)
			domains = domain_depth_map[depth]
			for domain in domains:
				print("  ", domain)
	
def main():
	blacklist = load_blacklist()
	check_for_duplicates(blacklist)
	check_for_overlaps(blacklist)

if __name__ == "__main__":
	main()

