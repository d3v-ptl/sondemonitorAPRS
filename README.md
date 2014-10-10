Sondemonitor to APRS Bridge
================

I track Bureau of Meteorology Radiosondes occasionally, and I figured it'd be nice to be able to push their position into APRS, for mapping on aprs.fi.

I'm going to assume you know how to use SondeMonitor, and know how to set it up to decode a position. If not, there's probably some guides online on how to do it.

Once you have Sondemonitor calculating/decoding positions, turn on the Google Earth "live server" feature (in Options).

Modify the appropriate variables in the python script (aprsUser and aprsPass being the important ones), and run it. You should now be pushing positions to APRS-IS!

Dependencies: Python 2.7/2.8, PyKML

Disclaimer: I wrote this to work with Vaisala RS92SGP sondes. I'm not sure if Sondemonitor's KML output changes with different sondes. If it does, this code will likely break horribly.

Some of my blog posts on tracking radiosondes:
http://rfhead.net/?p=42
http://rfhead.net/?p=550

