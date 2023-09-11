#!/usr/bin/env python3

# Autor: Miguel Erill
# Version: 0.1 (08/09/2023) Version inicial
#
#
# Call it with a list of monitors to include or nothing to include all
#
# Example:
#    kuma2influx.py               - Output all monitors retrieved
#    kuma2influx.py monit1 monit2 - Output only monit1 and monit2 data
#
# You can use regular expressions to filter like:
#    kuma2influx.py monit* - Output all monitors starting with monit
#
# Filter is case sensitive. Some filters need to be enclosed in quotes:
#
#   if they contain blanks: "my monitor"
#   if they use special chars: "*t"
#
# In general, quoting filters is safer
#

import sys
import requests
import fnmatch

# Where to get the data from
URL = "http://xx.xx.xx.xx:3001/metrics"
# Access data for Uptime Kuma. Create an API key in the Kuma console
API_TOKEN = "your-kuma-api-token-here"

# Line headers: where is the information we want to consolidate?
HEADERS = [
  "monitor_cert_days_remaining",
  "monitor_cert_is_valid",
  "monitor_response_time",
  "monitor_status"
 ]

# The meassurement name you want to get in the output
M_NAME='up_kuma'


#
# Below this line you should not need to touch anyting unless you know what
# you are doing
#
def is_header(text):
  idx = 0
  for t in HEADERS:
    if t == text:
      return idx
    idx+=1
  return -1

resp = requests.get(URL, auth=("",API_TOKEN))

if resp.status_code == 200:

  monitors = {}
  args = sys.argv[1:]
  n_param = len(args)

  for line in resp.iter_lines():
    if line and line[0] != '#':  # Avoid scanning comments
      decoded = line.decode('utf8').split('{')
      p = is_header(decoded[0]) # Do we have a match?
      if p >= 0:
        s = decoded[1].split("}")
        fields = s[0].split(",")
        d = dict(tuple(i.split('=')) for i in fields)
        name = d['monitor_name'].strip('\"')
        # Include only listed monitors, if any, or all if empty
        if n_param > 0 and not any(fnmatch.fnmatch(name, patrn) for patrn in args):
          continue
        monitors.setdefault(name, {}).setdefault('type', d['monitor_type'].strip('\"'))
        if p == 0: # Cert days remaining
          monitors[name]['url'] = d['monitor_url'].strip('\"')
          monitors[name]['cert_days'] = s[1].strip()
        elif p == 1: # cert valid?
          monitors[name]['cert_valid'] = s[1].strip()
        elif p == 2: # response time
          monitors[name]['host'] = d['monitor_hostname'].strip('\"')
          monitors[name]['resp_time'] = s[1].strip()
          monitors[name].setdefault('url', '')
        elif p == 3: # monitor status: 0..3
          monitors[name]['status'] = s[1].strip()

# We already got all info consolidated and organized. Now print output
  for m_id, m_info in monitors.items():
    v_or_m = '1i' if (m_info['status']=='1' or m_info['status']=='3') else '0i'
    if m_info.get('cert_days') != None:
      # HTTPS monitors return additional set of values
      print (M_NAME+',monitor='+m_id+',type='+m_info['type']+' host="'+m_info['host']+'",resp_time='+m_info['resp_time']+',status='+m_info['status']+'i,up_or_maintenance='+v_or_m+',url='+m_info['url']+',days='+m_info['cert_days']+'i,valid='+m_info['cert_valid']+'i')
    else:
      print (M_NAME+',monitor='+m_id+',type='+m_info['type']+' host="'+m_info['host']+'",resp_time='+m_info['resp_time']+',status='+m_info['status']+'i,up_or_maintenance='+v_or_m)
