import os
import re
import time
import urllib.request
import warnings

from bs4 import BeautifulSoup
from cairosvg import svg2png
from ebooklib import epub
import pandas as pd
from PIL import Image
from yattag import Doc, indent

def handle_img(source_url):
    # This function checks if the requested image has been downloaded and does
    # so if it hasn't. It then resizes the image to 758px wide if it is wider. It
    # then saves the file as a JPEG to `images_small` and returns the file path

    file_name, file_ext = os.path.splitext(source_url.split('/')[-1])

    file_path_original = 'images_original/{}{}'.format(file_name, file_ext)
    file_path_small = 'images_small/{}.jpg'.format(file_name)

    if not os.path.isfile(file_path_small):
        # Download the file if it hasn't been already
        if not os.path.isfile(file_path_original):
            _, headers = urllib.request.urlretrieve(source_url, file_path_original)
            # sleep for 0.5 seconds to not overload the servers with requests
            time.sleep(0.5)

        if file_ext == '.svg':
            png_path = file_path_original.replace('.svg', '.png')

            # Rasterize an SVG file to a PNG that PIL can then handle
            svg2png(
                url=file_path_original,
                write_to=png_path,
                unsafe=True
            )

            file_path_original = png_path

        with Image.open(file_path_original, mode='r') as img:
            # Resize to fit within my Kobo Aura's resolution (758×1014)
            max_height, max_width = 1014, 758
            img_height, img_width = img.size

            if img_height > max_height or img_width > max_width:
                height_ratio = max_height / img_height
                width_ratio = max_width / img_width
                ratio = min(height_ratio, width_ratio)
                img = img.resize(
                    size=(
                        int(round(img_height * ratio)),
                        int(round(img_width * ratio))),
                    resample=Image.LANCZOS)
                # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters

            # Set to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # This will convert the file to JPEG based if needed
            img.save(file_path_small)

    return file_path_small

# The pickle file the contents should be read from
contents = pd.read_pickle('./contents.pkl')

# The EpubBook object to write to
book = epub.EpubBook()

# Set metadata
book.set_identifier('teachastronomy.com')
book.set_title('Teach Astronomy')
book.set_language('en')
book.add_author('Impey, Chris')
book.spine = ['nav'] # Chapters will be appended later
book.set_cover('cover.jpg', open('cover.jpg', 'rb').read())

# Collect all chapters and sections in this list
book_toc = []

# Loop through all chapters
for chapter_index, chapter in contents.iterrows():
    chapter_title = '{}. {}'.format(
        chapter_index + 1,
        chapter['humanchapter'])
    chapter_file_name = 'chap_{0:02d}.xhtml'.format(chapter_index + 1)

    print('{}'.format(chapter_title))

    # Set up en EPUB chapter, ...
    epub_chapter = epub.EpubHtml(
        title=chapter_title,
        file_name=chapter_file_name)

    # ... add it to the table of contents
    book_toc.append(epub.Link(
        href=chapter_file_name,
        title=chapter['humanchapter'],
        uid=chapter_file_name.split('.')[0]))

    # ... and compile the HTML contents for it
    doc, tag, text = Doc().tagtext()

    with tag('h1'):
        text(chapter_title)

    for section_index, section in chapter['sections'].iterrows():
        section_title = '{}.{} {}'.format(
            chapter_index + 1,
            section_index + 1,
            section['section'])

        print('{}'.format(section_title))

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
                        img_path = handle_img(img_src)
                        img_name, img_ext = os.path.splitext(img_path.split('/')[-1])
                        epub_img_path = 'images/{}{}'.format(img_name, img_ext)

                        # Add the image to the EPUB, if it isn't already
                        if book.get_item_with_href(epub_img_path):
                            warnings.warn('{} has already been added'.format(
                                img_path))
                        else:
                            epub_img = epub.EpubImage()
                            epub_img.uid = img_name
                            epub_img.file_name = epub_img_path

                            if img_ext == '.jpg':
                                epub_img.media_type = 'image/jpeg'
                            else:
                                raise ValueError('You\'re adding something that isn\'t a JPEG')

                            with open(img_path, 'rb') as img_bin:
                                epub_img.content = img_bin.read()

                            book.add_item(epub_img)

                        if div_caption:
                            img_caption = div_caption.text.strip()
                            doc.stag('img', src=epub_img_path, alt=img_caption)
                            with tag('figcaption'):
                                with tag('em'):
                                    text(img_caption)
                        else:
                            doc.stag('img', src=epub_img_path)

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

        section_author = section_soup.find(id='book-page-authors')
        if section_author:
            with tag('p'):
                with tag('em'):
                    text(section_soup.find(id='book-page-authors').text.strip())

    # Add the HTML to the chapter and the chapter to the book
    epub_chapter.content = indent(doc.getvalue())
    book.add_item(epub_chapter)
    book.spine.append(epub_chapter)

# add table of contents
book.toc = tuple(book_toc)

# add CSS
style = 'img {max-width: 100%; max-height: 100%}'
nav_css = epub.EpubItem(
    uid='style_nav',
    file_name='style/nav.css',
    media_type='text/css', content=style)
book.add_item(nav_css)

# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# write to the file
epub.write_epub('Impey, Chris - Teach Astronomy.epub', book, {})
