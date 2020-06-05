import time

# Install these through pip or conda
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Load the result from get_index.py into a dataframe
index = pd.read_pickle('./index.pkl')

base_url = 'https://www.teachastronomy.com/textbook/'

# Construct URLs for each section and download its contents
for chapter_index, chapter in index.iterrows():
    for section_index, section in chapter['sections'].iterrows():
        section_url = '{}{}/{}/'.format(
            base_url,
            chapter['urlchaptertitle'],
            section['urlpagetitle'])

        response = requests.get(section_url)

        if not response.ok:
            raise ValueError('{} [{}] for {}'.format(
                response.status_code,
                response.reason,
                response.url))
        else:
            print('{} [{}] for {}'.format(
                response.status_code,
                response.reason,
                response.url))

        soup = BeautifulSoup(response.text, 'html.parser')
        section_contents = soup.find_all(id='book-page')[0].prettify()
        section['contents'] = section_contents

        # sleep for 0.5 seconds to not overload the servers with requests
        time.sleep(0.5)

# Now that index contains all contents, save it to another pickle
index.to_pickle('./contents.pkl')