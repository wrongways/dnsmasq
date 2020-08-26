# dnsmasq
Tools to parse dnsmasq logfile, generate a hosts file and to optimize blacklists

* inspect_hosts.py: looks for dodgy keywords (track, pixel...) in the hosts file and for each one it finds asks if it should be deleted
* hosts_from_log.py: extracts the ip addresses from the reply stanzas in /var/log/dnsmasq.log and uses it to populates the hosts file - effectively making the hosts file a long-term cache provided that the domain is not blacklisted. Thus the log file should be periodically deleted and the hosts file repopulated
blacklist.py: manipulates blacklists looking for duplicate and overlapping domain entries and provides some utility functions used by hosts_from_log.py
* update_conf_files.py: old code not maintained
