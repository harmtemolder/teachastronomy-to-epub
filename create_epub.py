import os
import re
import time
import urllib.request

from bs4 import BeautifulSoup
from ebooklib import epub
import pandas as pd
from yattag import Doc, indent

# The pickle file the contents should be read from
contents = pd.read_pickle('./contents.pkl')

# The EpubBook object to write to
book = epub.EpubBook()

# Set metadata
book.set_identifier('teachastronomy.com')
book.set_title('Teach Astronomy')
book.set_language('en')

book.add_author('Chris Impey')
book.spine = ['nav'] # Chapters will be appended later

# Loop through all chapters
for chapter_index, chapter in contents.iterrows():
  chapter_title = '{}. {}'.format(
      chapter_index + 1,
      chapter['humanchapter'])

  # Set up en EPUB chapter...
  epub_chapter = epub.EpubHtml(
    title=chapter_title,
    file_name='chap_{0:02d}.xhtml'.format(chapter_index + 1))

  # ... and compile the HTML contents for it
  doc, tag, text = Doc().tagtext()

  with tag('h1'):
    text(chapter_title)

  for section_index, section in chapter['sections'].iterrows():
    section_title = '{}.{} {}'.format(
        chapter_index + 1,
        section_index + 1,
        section['section'])

    # Start every section with an H2 section title
    with tag('h2'):
      text(section_title)

    # Parse every paragraph of the section one-by-one
    section_soup = BeautifulSoup(section['contents'], 'html.parser')
    section_paragraphs = section_soup.find(id='book-page-contents').contents

    for paragraph in section_paragraphs:
      if (hasattr(paragraph, 'attrs') and
          'class' in paragraph.attrs and
          ('book-paragraph-wrapper' in paragraph.attrs['class'] or
           'astropedia-image-container' in paragraph.attrs['class'])):

        # These special paragraphs usually contain an image, ...
        img = paragraph.find('img')  # Note that I only keep the first

        # ... sometimes with a div with an alt attribute, ...
        div_caption = paragraph.find('div', 'astropedia-image-caption')

        if img:
          with tag('figure'):
            img_src = 'https:{}'.format(img['src'].replace('/hrthumbs', ''))
            img_name = img_src.split('/')[-1]
            img_path = 'images/{}'.format(img_name)
            img_ext = img_name.split('.')[-1].lower()

            # Download the image if it hasn't been already
            if not os.path.isfile(img_path):
              _, headers = urllib.request.urlretrieve(img_src, img_path)
              print('{}: {}'.format(img_name, headers.get('Connection')))

              # sleep for 0.5 seconds to not overload the servers with requests
              time.sleep(0.5)

            # Add the image to the EPUB
            epub_img = epub.EpubImage()
            epub_img.uid = img_name.split('.')[0]
            epub_img.file_name = 'images/{}'.format(img_name)

            if img_ext == 'jpg' or img_ext == 'jpeg':
              epub_img.media_type = 'image/jpeg'
            elif img_ext == 'png':
              epub_img.media_type = 'image/png'
            elif img_ext == 'gif':
              epub_img.media_type = 'image/gif'
            elif img_ext == 'svg':
              epub_img.media_type = 'image/svg+xml'
            else:
              raise IOError('You are trying to add a non-standard image')

            with open(img_path, 'rb') as img_bin:
              epub_img.content = img_bin.read()

            book.add_item(epub_img)

            if div_caption:
              img_caption = div_caption.text.strip()
              doc.stag('img', src=img_path, alt=img_caption)
              with tag('figcaption'):
                text(img_caption)
            else:
              doc.stag('img', src=img_path)

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

  # Add the HTML to the chapter and the chapter to the book
  epub_chapter.content = indent(doc.getvalue())
  book.add_item(epub_chapter)
  book.spine.append(epub_chapter)

# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# write to the file
epub.write_epub('Impey, Chris - Teach Astronomy.epub', book, {})
