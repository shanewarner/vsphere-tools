#!/usr/bin/python
import os
import sys
import re
import argparse
import json
import getpass
from pysphere import VIServer,MORTypes

phase1_vcenters = {'DFW': '172.16.34.60',
  'RWC': '172.17.34.60',
  'LIS': '172.18.34.60',
  'SEC': '172.19.34.60'}

phase2_vcenters = {'RDCY': '172.20.0.60',
  'ALLN': '172.20.32.60',
  'SNDG': '172.21.0.60',
  'STLS': '172.21.32.60',
  'LOND': '172.22.0.60',
  'AMST': '172.22.32.60',
  'TKYO': '172.23.0.60',
  'HNKG': '172.23.32.60'}

vcenters = dict(phase1_vcenters, **phase2_vcenters)

def vcenter_lookup(site):
 for site1,ip in vcenters.iteritems():
   if site in site1:
     result = {site: ip}
     return result

 print "Invalid site selected."
 print "Valid sites are:"
 print "----------------"
 for site1,ip in vcenters.iteritems():
   print site1
 sys.exit(-1)

def main():
  parser = argparse.ArgumentParser(description='Roster_builder builds out an YAML roster file by querying vcenter for the specified regex.')
  parser.add_argument("-r", "--regex", help="Regex search string. Example: \"dfw1-access0[0-9].*\"", default=".*")  
  parser.add_argument("-u", "--username", help="Vcenter username.", default="admin")
  parser.add_argument("-c", "--cluster", help="Specify cluster to grab node data for. Ex: ACDP")
  parser.add_argument("-s", "--site", help="Build a roster for a specific site.", default=0)
  parser.add_argument("-f", "--file", help="Name of roster file to write to [Default: roster.txt]", default="roster.txt")
  args = parser.parse_args()

  server = VIServer()
  properties = ['name', 'summary.runtime.powerState', 'config.guestFullName', 'guest.ipAddress', 'guest.hostName', 'guest.toolsRunningStatus']
  hosts = []
  vmlist = []
  regex = args.regex

  f = open(args.file, 'w')

  if args.site:
    site_dict = vcenter_lookup(args.site)
    print "Using site data: ",site_dict
  else:
    site_dict = vcenters

  print "Enter vcenter password for", args.username
  password = getpass.getpass('Password:')

  for site,ip in site_dict.iteritems():
    print site, ip
    server.connect(ip, args.username, password)

    f.write(site + ':\n')
    if args.cluster is None:
    	clusters = server.get_clusters().iteritems()
    else:
        clusters = { "key": args.cluster }.iteritems()

    for key, value in clusters:
      cluster = [k for k,v in server.get_clusters().iteritems() if v==value]
      print "Cluster: ",value

      for node in cluster:
        vmlist = server._retrieve_properties_traversal(
          property_names=properties,
          from_node=node,
          obj_type=MORTypes.VirtualMachine)

      if vmlist is None:
        continue

      f.write('  '+value+':\n')

      for vm in vmlist:
        try:
          prop_set = vm.PropSet
        except AttributeError:
          continue

        for prop in prop_set:
          if prop.Name == 'summary.runtime.powerState':
            powerState = prop.Val
          elif prop.Name == 'guest.hostName':
            hostName = prop.Val
          elif prop.Name == 'config.guestId':
            guestId = prop.Val
          elif prop.Name == 'guest.ipAddress':
            ipAddress = prop.Val
          elif prop.Name == 'name':
            name = prop.Val
          elif prop.Name == 'guest.toolsRunningStatus':
            toolsRunningStatus = prop.Val

        if powerState == 'poweredOff':
          toolsRunningStatus = 'poweredOff'
 
        if re.search(regex,hostName):
          f.write('   '+ hostName + ':\n')
          f.write('      ipAddress: ' + ipAddress + '\n')
          f.write('      powerState: ' + powerState + '\n')
          f.write('      toolsRunningStatus: ' + toolsRunningStatus + '\n')

if __name__ =='__main__':
  main()
