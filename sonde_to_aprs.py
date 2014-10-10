#!/bin/bash
# Oh wait, you'll usually be running this on Windows :-)
#
# Sondemonitor to APRS bridge
# Copyright (C) 2014 Mark Jessop <vk5qi@rfhead.net>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import time, datetime, urllib2
from pykml import parser
from socket import *

# Sondemonitor URL
sm_url = "http://127.0.0.1:4190/sm_google.kml"

# APRS-IS login info
serverHost = 'rotate.aprs2.net' # Pick a local server if you like
serverPort = 14580

aprsUser = 'NOCALL' # Replace with your own callsign. This should NOT have any SSID's on it (i.e. -9)
aprsPass = '12345' # APRS-IS passcode for your callsign.

# APRS packet Settings
callsign = aprsUser # This is the callsign the object comes from. Doesn't necessarily have to be the same as your APRS-IS login. 
update_rate = 30 # Update rate, in seconds.

# Get KML from SondeMonitor and parse into a Python dictionary
def get_sonde():
	sonde_data = {}
	sonde_data["valid"] = False
	sonde_data["lat"] = "0.00000"
	sonde_data["lon"] = "0.00000"
	sonde_data["alt"] = "00000"
	sonde_data["id"] = "Unknown"
	sonde_data["temp"] = "0.0"
	sonde_data["freq"] = "XX.XXMHz"
	sm_f = urllib2.urlopen(sm_url)
	sm_data = sm_f.read()
	if len(sm_data)==0:
		print "No data from SM."
	else:
		try:
			root = parser.fromstring(sm_data)
			if(root.Document.Placemark[0].description == "Sonde"):
				# We have something...
				sm_name = str(root.Document.Placemark[0].name).split(" ")
				sm_coords = str(root.Document.Placemark[0].Point.coordinates).split(",")
				sonde_data["freq"] = sm_name[2][1:-1]
				sonde_data["lon"] = sm_coords[0]
				sonde_data["lat"] = sm_coords[1]
				sonde_data["alt"] = sm_coords[2]
				sonde_data["id"] = sm_name[1]
				sonde_data["temp"] = sm_name[-1] # Last field is temp.
				sonde_data["valid"] = True
				return sonde_data
			else:
				print "Fail"
		except:
			print "Something didn't parse right"
			return sonde_data

# Push a Radiosonde data packet to APRS as an object.
def push_balloon_to_aprs(sonde_data):
	# Pad or limit the sonde ID to 9 characters.
	object_name = sonde_data["id"]
	if len(object_name) > 9:
		object_name = object_name[:9]
	elif len(object_name) < 9:
		object_name = object_name + " "*(9-len(object_name))
	
	# Convert float latitude to APRS format (DDMM.MM)
	lat = float(sonde_data["lat"])
	lat_degree = abs(int(lat))
	lat_minute = abs(lat - int(lat)) * 60.0
	lat_min_str = ("%02.2f" % lat_minute).zfill(5)
	lat_dir = "S"
	if lat>0.0:
		lat_dir = "N"
	lat_str = "%02d%s" % (lat_degree,lat_min_str) + lat_dir
	
	# Convert float longitude to APRS format (DDDMM.MM)
	lon = float(sonde_data["lon"])
	lon_degree = abs(int(lon))
	lon_minute = abs(lon - int(lon)) * 60.0
	lon_min_str = ("%02.2f" % lon_minute).zfill(5)
	lon_dir = "E"
	if lon<0.0:
		lon_dir = "W"
	lon_str = "%03d%s" % (lon_degree,lon_min_str) + lon_dir
	
	# Convert Alt (in metres) to feet
	alt = int(float(sonde_data["alt"])/0.3048)
	
	# Produce the APRS object string.
	out_str = ";%s*111111z%s/%sO000/000/A=%06d BOM Balloon %s" % (object_name,lat_str,lon_str,alt, sonde_data["freq"])
	print out_str
	
	# Connect to an APRS-IS server, login, then push our object position in.
	
	# create socket & connect to server
	sSock = socket(AF_INET, SOCK_STREAM)
	sSock.connect((serverHost, serverPort))
	# logon
	sSock.send('user %s pass %s vers VK5QI-Python 0.01\n' % (aprsUser, aprsPass) )
	# send packet
	sSock.send('%s>APRS:%s\n' % (callsign, out_str) )
	
	# close socket
	sSock.shutdown(0)
	sSock.close()

sonde_data_old = get_sonde()

# Now we start parsing data from SM and sending it through.
while 1:
	sonde_data_new = get_sonde()
	# Test if we have new data.
	if(sonde_data_new["lat"] != sonde_data_old["lat"] and sonde_data_new["lon"] != sonde_data_old["lon"] and sonde_data_new["alt"] != sonde_data_old["alt"]):
		#time_now = datetime.datetime.utcnow()
		#time_str = time_now.strftime("%H:%M:%S")
		#seq_no += 1
		#out_str = "$$$$$%s,%d,%s,%s,%s,%s,%s,%s*0000" % (callsign,seq_no,time_str,sonde_data_new["lat"],sonde_data_new["lon"],sonde_data_new["alt"], sonde_data_new["temp"], sonde_data_new["id"])
		#print out_str
		#conn.sendall(out_str + "\n")
		try:
			push_balloon_to_aprs(sonde_data_new)
		except:
			print "Couldn't push data to APRS"
		sonde_data_old = sonde_data_new
		time.sleep(update_rate)
	else:
		print "No new data."
	time.sleep(1)

	
