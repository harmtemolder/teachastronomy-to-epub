import ebooklib
from bs4 import BeautifulSoup
import bleach
import pandas as pd
from yattag import Doc

doc, tag, text = Doc().tagtext()

contents = pd.read_pickle('./contents.pkl')

for chapter_index, chapter in contents.iterrows():
    # Start every chapter with an H1 chapter title
    with tag('h1'):
        text('{}. {}'.format(
            chapter['chapterid'],
            chapter['humanchapter']))

    for section_index, section in chapter['sections'].iterrows():
        # Start every section with an H2 section title
        with tag('h2'):
            text('{}.{}. {}'.format(
                chapter['chapterid'],
                section['pageid'],
                section['section']))

        # Parse every paragraph of the section one-by-one
        section_soup = BeautifulSoup(section['contents'], 'html.parser')
        section_paragraphs = section_soup.find_all(id='book-page-contents')[0].contents

        for paragraph in section_paragraphs:
            if paragraph == '\n':
                # Skip empty paragraphs
                continue

            elif ('class' in paragraph.attrs
                  and 'book-paragraph-wrapper' in paragraph['class']):
                # These special paragraphs usually contain images, ...
                imgs = paragraph.find_all('img')
                if imgs:
                    img_src = 'https:{}'.format(
                        imgs[0]['src'].replace('/hrthumbs', ''))

                    with tag('p'):
                        doc.stag('img', src=img_src)

                    # Note that I only keep the first image

                # ... usually followed by a p of text, which can be cleaned
                # like regular paragraphs
                ps = paragraph.find_all('p')
                if ps:
                    paragraph = ps[0]
                else:
                    continue

            # Clean the paragraph
            clean_paragraph = bleach.clean(
                paragraph.prettify(),
                tags=['p'],
                strip=True)

            clean_paragraph = ' '.join(str(clean_paragraph).replace('\n', '').split())

            # doc.asis(' '.join(str(paragraph).replace('\n', '').split()))
            print(clean_paragraph)
            doc.asis(clean_paragraph)

            pass
        pass
    pass

with open('./teachastronomy.html', 'w') as output_html:
    output_html.write(doc.getvalue())

# TODO Check result with https://code.google.com/archive/p/epubcheck/