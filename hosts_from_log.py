#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

import re
import socket
from pathlib import Path


logfile = '/var/log/dnsmasq.log'
hostfile = 'hosts'


def is_ipaddress(host):
	return is_ipv4(host) or is_ipv6(host)

def is_ipv6(host):
	ipv6_regex = re.compile('^[0-9a-fA-F:]+$')
	return ipv6_regex.match(host) != None
	
def is_ipv4(host):
	ipv4_regex = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
	return ipv4_regex.match(host) != None

def show_progress(current, total):
	CGREY    = '\33[90m'
	CGREEN  = '\33[32m'
	CEND      = '\33[0m'
	done = round(current * 100 / total)
	remaining = 100 - done
	print(f"\r{CGREEN}{'|' * done}{CGREY}{'|' * remaining}{CEND} {done}%", end="")
	
	
	
def hosts_from_logfile(logfile):
	# Find all unique hosts in log

	print(f"Searching {logfile} for dns queries")
	hosts = set()
	with open(logfile) as f:
		for line in f:
			fields = line.split()
			action = fields[4]
		
			if action.startswith('reply'):
				host = fields[5]
				address = fields[7]
				if address[0].isnumeric():
					if not (is_ipaddress(host) or host.endswith("arpa")):
						hosts.add(host.lower())
				else:
					print(address)
				
	return hosts


def is_blacklisted(host, blacklist):
	for domain in blacklist:
		if host.endswith(domain):
			return True
	
	return False


def load_blacklist():
	blacklisted_domains = set()
	cwd = Path('.')
	for conffile in cwd.glob('*.conf'):
		with open(conffile) as f:
			for line in f:
				if line.startswith('address'):
					domain = line.split("/")[1]
					blacklisted_domains.add(domain.lower())
	
	return blacklisted_domains


def remove_blacklisted_hosts(hosts, blacklist):
	to_delete = set()
	for host in hosts:
		if is_blacklisted(host, blacklist):
			to_delete.add(host)
	
	for host in to_delete:
		hosts.remove(host)

def sorted_hosts(hosts):
	reverse_domain = [".".join(reversed(host.split("."))) for host in hosts]
	reverse_domain = sorted(reverse_domain)
	return [".".join(reversed(host.split("."))) for host in reverse_domain]
		
hosts = hosts_from_logfile(logfile)
print("=" * 120)
hosts_count = len(hosts)
print(f"Identified {hosts_count:,} distinct hosts")
blacklist = load_blacklist()
remove_blacklisted_hosts(hosts, blacklist)
deleted_hosts = hosts_count - len(hosts)
print(f"Found {deleted_hosts:,} blacklisted hosts")
print(f"Now have {len(hosts):,} remaining")
						
for host in sorted_hosts(hosts)[:80]:
	print(host.rjust(48))		

# with open(hostfile, "w") as f:
# 	for host, address in lookup_map.items():
# 		print(f"{address} {host}", file=f)
# 
# print(f"\nSaved {len(lookup_map):,}/{len(hosts):,} addresses")
# 



# 
# # Lookup each address 
# lookup_map = {}
# for i, host in enumerate(sorted(list(hosts))):
# 	
# 	show_progress(i, len(hosts))
# 	
# 	try:
# 		ip_addresses = socket.getaddrinfo(host,  0)
# 		
# 		# The return from getaddrinfo is a list of records
# 		# The last entry of each record contains a tuple,
# 		# the first element of which is the ip address
# 		#
# 		# Will use the address given in the first record
# 		
# 		ip_address = ip_addresses[0][-1][0]
# 		
# 		# if the ip_address == '::', it's blocked, ignore
# 		if ip_address != '::':
# 			lookup_map[host] = ip_address
# 	except:
# 		continue
# # 		print(f"Failed to find {host}")

		

