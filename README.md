Various salt tools
------------------

Usage
------------------
usage: roster_builder.py [-h] -r REGEX [-u USERNAME] [-s SITE] [-f FILE]

Roster_builder builds out an salt-ssh roster file by querying vcenter for the
specified regex.

optional arguments:
  -h, --help            show this help message and exit
  -r REGEX, --regex REGEX
                        Regex search string. Example: "dfw1-access0[0-9].*"
  -u USERNAME, --username USERNAME
                        Vcenter username.
  -s SITE, --site SITE  Build a roster for a specific site.
  -f FILE, --file FILE  Name of roster file to write to [Default: roster.txt]
