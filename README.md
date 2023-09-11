# kuma2influx
Convert kuma metrics to influx format

A simple python script to read the metrics from kuma monitors and output them in influxdb format. You can then fire a telegraf instance with an [inputs.exec] area where you execute the script and send tha data to your influx instance. Later you can use grafana to show it.

# Why
My monitor stack is a TIG one so I have no prometheus. The only way I found to inject kuma data into a grafana console was through prometheus so I had to create my own script to be able to do it via influxdb.

This is an initial version so bear with me. I have only included the type of monitors that I am using so there my be many others fields that may be of interest for include. If you have any of these and need to include them please tell me. 

# What you need
An API key from your kuma host. Create the key in Settings->API Keys

![imagen](https://github.com/mikee2/kuma2influx/assets/5814118/f0cd9ef9-47d4-44a0-be27-b62754865b14)

Paste your key into the API_TOKEN reserved space. Adjust the URL or address where the kuma host is running. Take care of openning filrewall ports and make an static port assignment if you are running the script from outside your local network.

Then open your telegraf.conf file and 
```
 [[inputs.exec]]
#   ## Commands array
   commands = [
     "/usr/bin/python3 /etc/telegraf/bin/kuma2influx.py server1 server2 dbserver*"
   ]
   interval = "60s"
   data_format = "influx"
```
Use the same interval that you configured into your monitors. It make no sense to request metrics every 5 seconds if you are testing them every minute. You will get 12 results that are the same. If you don't add names after the script you will retrieve the metrics of all existing monitors.

For the command line you can use a direct exec if the script is in a folder accsesible by the telegraf user (and with the correct rights)

     "/usr/bin/python3 /etc/telegraf/bin/kuma2influx.py server1 server2 dbserver*"

or else sudo it

     "sudo /usr/bin/python3 /etc/telegraf/bin/kuma2influx.py server1 server2 dbserver*"

In this case you would need to have sudo installed and configure visudo with 

```
Defaults:telegraf !requiretty, !syslog
telegraf ALL = NOPASSWD: /<script_path>/kuma2influx.py
```
