# teachastronomy-to-epub
 Download all content from the teachastronomy.com textbook to an epub file so I can read it offline

## It uses the following libraries, so make sure these are installed in your `env`
* `pandas`
* `bs4`
* `requests`
* `ebooklib`
* `yattag`

## Follow these steps:
1. Use `get_index.py` to create a dataframe of dataframes (sections per chapter)
1. Use `get_contents.py` to add the actual contents of each section to that dataframe
1. ~~Use `create_html.py` to convert those contents to a single HTML file~~
1. ~~Use `get_images.py` to download all referenced images and create a new, offline HTML file~~
1. Use `create_epub.py` to convert those contents to an EPUB file and download all referenced images
