#!/bin/zsh
grep reply /var/log/dnsmasq.log | 			\
	awk '{print $8, $6}' | 					\
	egrep -v "(CNAME|NODATA|NX|SERVFAIL)" | \
	sort -uV | 								\
	egrep -v "^[^0-9]"
