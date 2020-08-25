#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

import re
import socket
from pathlib import Path
from optimize_blacklist import load_blacklist, is_blacklisted, sorted_domain_dict

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


######################
# NOT CURRENTLY USED
######################
def lookup_hosts(hosts):
	# Lookup each address

	lookup_map = {}
	for i, host in hosts.enumerate():

		show_progress(i, len(hosts))

		try:
			ip_addresses = socket.getaddrinfo(host,  0)

			# The return from getaddrinfo is a list of records
			# The last entry of each record contains a tuple,
			# the first element of which is the ip address
			#
			# Will use the address given in the first record

			ip_address = ip_addresses[0][-1][0]

			# if the ip_address == '::', it's blocked, ignore
			if ip_address != '::':
				lookup_map[host] = ip_address
		except:
			continue

	return lookup_map

def hosts_from_logfile(logfile):
	# Find all unique hosts in log
	# Overwrites old addresses with new ones

	print(f"Searching {logfile} for dns queries")
	hosts = {}
	with open(logfile) as f:
		for line in f:
			fields = line.split()
			action = fields[4]

			if action.startswith('reply'):
				host = fields[5]
				address = fields[7]
				if address[0].isnumeric():
					if not (is_ipaddress(host) or host.endswith("arpa")):
						hosts[host.lower()] = address

	return hosts


def remove_blacklisted_hosts(hosts, blacklist):
	to_delete = set()
	for host in hosts:
		if is_blacklisted(host, blacklist):
			to_delete.add(host)

	for host in to_delete:
		del hosts[host]

def print_hosts(hosts):
	for host, address in hosts.items():
		print(f"{host.rjust(48)}: {hosts[host]}")

def save_hosts(hosts):
	with open(hostfile, "w") as f:
		for host, address in hosts.items():
			print(f"{address} {host}", file=f)


def main():
	blacklist = set(load_blacklist().keys())
	hosts = hosts_from_logfile(logfile)
	hosts_count = len(hosts)
	print()
	remove_blacklisted_hosts(hosts, blacklist)
	deleted_hosts = hosts_count - len(hosts)
	print(f"Identified {hosts_count:,} distinct hosts, of which {deleted_hosts:,} are blacklisted")
	print(f"{len(hosts):,} hosts remaining")

	hosts = sorted_domain_dict(hosts)
	save_hosts(hosts)
	print(f"\nSaved {len(hosts):,} addresses to {hostfile}")

if __name__ == '__main__':
	main()
