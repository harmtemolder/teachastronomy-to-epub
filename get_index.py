# This script will get all sections of all chapters and save them to a pickle
# file which can then be used to get each section's contents

from bs4 import BeautifulSoup
import pandas as pd
import requests

result = pd.DataFrame(columns=[
    'urlchaptertitle',
    'chapterid',
    'humanchapter',
    'sections'
])

url = 'https://www.teachastronomy.com/textbook/'
response = requests.get(url)

if not response.ok:
    raise ValueError(
        '{} [{}] for {}'.format(
            response.status_code,
            response.reason,
            response.url))

soup = BeautifulSoup(response.text, 'html.parser')
soup_tree = soup.find_all(id='book-tree')
soup_chapters = soup_tree[0].find_all(class_='book-tree-chapter')

# Loop through each chapter and add it's sections (i.e. pages) to result

for chapter in soup_chapters:
    chapter_sections = pd.DataFrame(columns=[
        'pageid',
        'pageorder',
        'bruteorder',
        'urlpagetitle',
        'entryid',
        'section',
        'contents'])

    soup_sections = chapter.find_all(class_='book-tree-section')

    for section in soup_sections:
        section_result = pd.Series(
            index=[
                'pageid',
                'pageorder',
                'bruteorder',
                'urlpagetitle',
                'entryid',
                'section',
                'contents'],
            data=[
                section.attrs['data-pageid'],
                section.attrs['data-pageorder'],
                section.attrs['data-bruteorder'],
                section.attrs['data-urlpagetitle'],
                section.attrs['data-entryid'],
                section.text.strip(),
                ''])
        chapter_sections = chapter_sections.append(
            section_result,
            ignore_index=True)

    chapter_result = pd.Series(
        index=[
            'urlchaptertitle',
            'chapterid',
            'humanchapter',
            'sections'],
        data=[
            chapter.attrs['data-urlchaptertitle'],
            chapter.attrs['data-chapterid'],
            chapter.attrs['data-humanchapter'],
            chapter_sections
        ])

    result = result.append(chapter_result, ignore_index=True)

# Save and print result

result.to_pickle('./index.pkl')
print(result)
