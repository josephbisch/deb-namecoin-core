#
# Regular cron jobs for the namecoin-core package
#
0 4	* * *	root	[ -x /usr/bin/namecoin-core_maintenance ] && /usr/bin/namecoin-core_maintenance
