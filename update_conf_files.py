#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import re
import socket
from pathlib import Path
import matplotlib.pyplot as plt


logfile_name = 'dnsmasq.log'
blacklist = 'blacklist.conf'


def sort_domains_by_fqn(domain_list, reverse=False):
# 	reverse the order of the qualified name
	hosts = ['.'.join(host.split('.')[::-1]) for host in domain_list]
	hosts.sort(reverse=reverse)
	hosts = ['.'.join(host.split('.')[::-1]) for host in hosts]
	return hosts
	
	

# Logfile format:
# 		dnsmasq: query[A] self.events.data.microsoft.com from 192.168.1.3
# 		dnsmasq: config self.events.data.microsoft.com is 0.0.0.0
# 		dnsmasq: query[A] pubads.g.doubleclick.net from 192.168.1.3


query_counts = {}
cached_counts = {}
blocked_counts = {}
hosts_counts = {}
replies = {}
hosts = {}

# This is inexact as it allows illegal addresses, but 
# is sufficient for this case
ip_regex = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')




with open(logfile_name) as logfile:
	last_reply_host = last_config_host = last_hosts_host = None
	for line in logfile:
		if line.startswith('dnsmasq:'):
			fields = line.strip().lower().split()
			if len(fields) == 5:
				dnsmasq, action, host, direction, address = fields
				if action.startswith('query'):
					query_counts[host] = query_counts.get(host, 0) + 1
				elif (action == 'cached') and (address[0].isnumeric()):
					cached_counts[host] = query_counts.get(host, 0) + 1
				elif action == 'reply':
					# A reply can contain multiple addresses
					# keep a track of last host and only count one per request
					if host != last_reply_host:
						last_reply_host = host
						# Ignore ipv6
						if (':' not in host) and not ip_regex.match(host):
							# Ensure that it's an address and not a tag
							if address[0].isnumeric():
								reply_addresses = replies.get(host, set())
								reply_addresses.add(address)
								replies[host] = reply_addresses
						
				elif action == 'config':
					# Only count one for multiple entries
					if host != last_config_host:
						last_config_host = host
						if address in ('nodata-ipv4', '127.0.0.1', '0.0.0.0', '::'):
							blocked_counts[host] = blocked_counts.get(host, 0) + 1
				
				elif action.startswith('/usr/local/etc/')  and address[0].isnumeric():
					# Count one for multiple entries
					if host != last_hosts_host:
						last_hosts_host = host
						hosts_counts[host] = hosts_counts.get(host, 0) + 1
					
					
# Create dictionary of hosts to addresses from hosts file
with open('hosts') as h:
	linenum = 0
	for line in h:
		linenum += 1
		line = line.strip()
		if (len(line) > 10) and (line[0].isnumeric() or line[0] == ':'):
			address, host = line.split()
			host_addresses = hosts.get(host, set())
			host_addresses.add(address)
			hosts[host] = host_addresses
			

# Merge data from hosts and replies
non_blocked_hosts = sort_domains_by_fqn(replies.keys())
blocked_hosts = set()

with open('hosts', 'w') as h:
	for host in non_blocked_hosts:
	
		# Ensure that the host is not now blocked (by change in blacklists)
		ip_address = socket.getaddrinfo(host,  0)[-1][-1][0]
		if ip_address not in ['0.0.0.0', '::']:
			host_addresses = hosts.get(host, set())
		
			# merge with set union of hosts and replies
			host_addresses |= replies[host]
		
			# Write out hosts file, one ip address, one host per line
			for address in host_addresses:
				h.write(f'{address.ljust(30)} {host}\n')
		
		# If null ip address we're blocked, don't save to hosts
		# Only write out each host once (not for every address)
		elif host not in blocked_hosts:
			blocked_hosts.add(host)
			print(f'Not putting {host} in to hosts as in block list')
			
print("Cleaned up hosts file")
				
# check for duplicates in conf files
here = Path('.')
longest_domain_path = 0
paths = {}
for conffile in here.glob('*.conf'):
	lines = []
	with open(conffile, 'r') as conf:
		domains = set()
		linenum = 0
		for line in conf:
			linenum += 1
			if line.startswith('address'):
				_, domain, __ = line.split('/')
				if domain in domains:
					print(f'{conffile}: removed duplicate domain {domain} at line {linenum}')
				else:
					domains.add(domain)
					lines.append(line)
					
				# Find longest domain Path
				longest_domain_path = max(longest_domain_path, len(domain.split('.')))
				path_len = len(domain.split('.'))
				path_entry = paths.get(path_len, [])
				path_entry.append(domain)
				paths[path_len] = path_entry
				
			else:
				# Keep comments and blank lines
				lines.append(line)
		
	# write out unique lines
	with open(conffile, 'w') as conf:
		conf.seek(0)
		for line in lines:
			conf.write(line)
			
# print(f'{longest_domain_path=}')
# for k in sorted(paths):
# 	print(k)
# 	for domain in paths[k]:
# 		print(f'\t{domain}')
# 

# Check for sub-domains covered by higher domains
sorted_paths = sorted(paths)
for i, k in enumerate(sorted_paths):
	if k != sorted_paths[-1]:
		for domain in paths[k]:
			for domain_len in sorted_paths[i+1:]:
				for sub_domain in paths[domain_len]:
					if sub_domain.split('.')[-k:] == domain.split('.'):
						print(f'Redundant {sub_domain} with {domain}')

# check for duplicate address in hosts
with open('hosts') as h:
	addresses = {}
	distinct_hosts = set()
	total_addresses = 0
	for line in h:
		if line[0].isnumeric() or (line[0] == ':'):
			total_addresses += 1
			address, host = line.strip().split()
			hosts = addresses.get(address, [])
			hosts.append(host)
			addresses[address] = hosts
			distinct_hosts.add(host)


	distinct_address = len(addresses.keys())
	total_hosts = 0
	for address in addresses:
		total_hosts += len(addresses[address])
		
	print(f'hosts total addresses: {total_addresses}')
	print(f'hosts distinct addresses: {distinct_address}')
	print(f'hosts distinct hosts: {len(distinct_hosts)}')

with open('allowed_hosts.txt', 'w') as f:
	for host in non_blocked_hosts:
		f.write(f'{host}\n')
			
with open('hosts_hosts.txt', 'w') as f:
	for host in hosts:
		f.write(f'{host}\n')
			



#Plot some stats
# top_count = 15
# query_counts = {k: v for k, v in sorted(query_counts.items(), key=lambda item: item[1], reverse=True)}
# top_sites = list(query_counts.keys())[:top_count]
# top_counts = list(query_counts.values())[:top_count]
# fig, ax = plt.subplots(figsize=(8,5))
# ax.bar(top_sites, top_counts)
# plt.xticks(rotation=90)
# fig.subplots_adjust(bottom=0.5)
# plt.title('Top queries')
# plt.show()
# plt.close()
# 
# blocked_counts = {k: v for k, v in sorted(blocked_counts.items(), key=lambda item: item[1], reverse=True)}
# top_sites = list(blocked_counts.keys())[:top_count]
# top_counts = list(blocked_counts.values())[:top_count]
# fig, ax = plt.subplots(figsize=(8,5))
# ax.bar(top_sites, top_counts)
# plt.xticks(rotation=90)
# fig.subplots_adjust(bottom=0.5)
# plt.title('Top blocks')
# plt.show()
# plt.close()
# 
# cached_counts = {k: v for k, v in sorted(cached_counts.items(), key=lambda item: item[1], reverse=True)}
# top_sites = list(cached_counts.keys())[:top_count]
# top_counts = list(cached_counts.values())[:top_count]
# fig, ax = plt.subplots(figsize=(8,5))
# ax.bar(top_sites, top_counts)
# plt.xticks(rotation=90)
# fig.subplots_adjust(bottom=0.5)
# plt.title('Top cache hits')
# plt.show()
# plt.close()
# 
# hosts_counts = {k: v for k, v in sorted(hosts_counts.items(), key=lambda item: item[1], reverse=True)}
# top_sites = list(hosts_counts.keys())[:top_count]
# top_counts = list(hosts_counts.values())[:top_count]
# fig, ax = plt.subplots(figsize=(8,5))
# ax.bar(top_sites, top_counts)
# plt.xticks(rotation=90)
# fig.subplots_adjust(bottom=0.5)
# plt.title('Top hosts hits')
# plt.show()
# plt.close()


		
	
