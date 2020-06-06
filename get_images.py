# Go through the HTML, download all images and change the references to the
# local files instead

import os
import time
import urllib.request

from bs4 import BeautifulSoup

with open('./teachastronomy.html', 'r') as online_html:
  soup = BeautifulSoup(online_html, 'html.parser')

imgs = soup.find_all('img')
for img in imgs:
  img_src = img['src']
  img_name = img_src.split('/')[-1]
  img_path = './images/{}'.format(img_name)

  # Download the image if it hasn't been already
  if not os.path.isfile(img_path):
    _, headers = urllib.request.urlretrieve(img_src, img_path)
    print('{}: {}'.format(img_name, headers.get('Connection')))

    # sleep for 0.5 seconds to not overload the servers with requests
    time.sleep(0.5)

  # Point the <img> to the downloaded image
  img['src'] = img_path

# Save the resulting HTML
with open('./teachastronomy-offline.html', 'w') as offline_html:
  offline_html.write(soup.prettify())