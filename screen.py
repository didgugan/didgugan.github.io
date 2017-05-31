import requests
import sys
from datetime import datetime, timedelta
import pytz
from PIL import Image
from StringIO import StringIO
import os
import logging

# python himawari.py
# stolen from https://gist.github.com/celoyd/39c53f824daef7d363db

# Fetch Himawari-8 full disks at a given zoom level and set as desktop.
# Valid zoom levels seem to be powers of 2, 1..16, and 20.
#
# To do:
# - Better errors (e.g., catch the "No Image" image).
# - Librarify.


# Tile size for this dataset:
width = 550
height = 550


# time = parse(sys.argv[1])
tz = pytz.timezone('UTC')
time = datetime.now(tz) - timedelta(minutes=40)

scale = 8
out = sys.argv[1]


base = 'http://himawari8.nict.go.jp/img/D531106/%sd/550' % (scale)

tiles = [[None] * scale] * scale

def pathfor(t, x, y):
    return "%s/%s/%02d/%02d/%02d%02d00_%s_%s.png" \
    % (base, t.year, t.month, t.day, t.hour, (t.minute / 10) * 10, x, y)


sess = requests.Session() # so requests will reuse the connection
png = Image.new('RGB', (width*scale, height*scale))

def fetch_and_set():
    for x in range(scale):
        for y in range(scale):
            path = pathfor(time, x, y)
            tiledata = sess.get(path).content
            tile = Image.open(StringIO(tiledata))
            png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))

    png.save(out, 'PNG')

    os.system("osascript -e 'tell application \"Finder\" to set desktop picture to POSIX file \"" + out + "\"'")
    os.system("killall Dock")

try:
    fetch_and_set()
except requests.exceptions.ConnectionError:
    logging.exception('')
    try:
        fetch_and_set()
    except requests.exceptions.ConnectionError:
        logging.exception('')