import re

from bs4 import BeautifulSoup
import pandas as pd
from yattag import Doc

doc, tag, text = Doc().tagtext()

contents = pd.read_pickle('./contents.pkl')

for chapter_index, chapter in contents.iterrows():
  # Start every chapter with an H1 chapter title
  with tag('h1'):
    text('{}. {}'.format(
      chapter_index + 1,
      chapter['humanchapter']))

  for section_index, section in chapter['sections'].iterrows():
    # Start every section with an H2 section title
    with tag('h2'):
      text('{}.{} {}'.format(
        chapter_index + 1,
        section_index + 1,
        section['section']))

    # Parse every paragraph of the section one-by-one
    section_soup = BeautifulSoup(section['contents'], 'html.parser')
    section_paragraphs = section_soup.find(id='book-page-contents').contents

    for paragraph in section_paragraphs:
      if (hasattr(paragraph, 'attrs') and
          'class' in paragraph.attrs and
          ('book-paragraph-wrapper' in paragraph.attrs['class'] or
           'astropedia-image-container' in paragraph.attrs['class'])):
        # These special paragraphs usually contain an image, ...
        img = paragraph.find('img') # Note that I only keep the first
        # ... sometimes with a div with an alt attribute, ...
        div_caption = paragraph.find('div', 'astropedia-image-caption')

        if img:
          with tag('figure'):
            img_src = 'https:{}'.format(img['src'].replace('/hrthumbs', ''))

            if div_caption:
              img_caption = div_caption.text.strip()
              doc.stag('img', src=img_src, alt=img_caption)
              with tag('figcaption'):
                text(img_caption)
            else:
              doc.stag('img', src=img_src)

          print(img_src)

        # ... and usually followed by a p of text
        p = paragraph.find('p')
        if p:
          paragraph = p
        else:
          continue

      if hasattr(paragraph, 'text'):
        if re.search('^\s*$', str(paragraph.text)):
          # Skip empty paragraphs
          continue

        paragraph_text = paragraph.text
        paragraph_text = ' '.join(paragraph_text.split())
        paragraph_text = paragraph_text.replace('\n', '')
        paragraph_text = paragraph_text.replace(' ,', ',')
        paragraph_text = paragraph_text.replace(' .', '.')


        with tag('p'):
          text(paragraph_text)

        print(paragraph_text)
    pass
  pass
pass

with open('./teachastronomy.html', 'w') as output_html:
  output_html.write(doc.getvalue())

# TODO Check result with https://code.google.com/archive/p/epubcheck/