# teachastronomy-to-epub
 Download all content from the teachastronomy.com textbook to an EPUB file so I can read it offline

## It uses the following libraries, so make sure these are installed in your `env`
* `pandas`
* `bs4`
* `requests`
* `ebooklib`
* `yattag`
* `Pillow`
* `cairosvg`

## Follow these steps:
1. Use `get_index.py` to create a dataframe of dataframes (sections per chapter)
1. Use `get_contents.py` to add the actual contents of each section to that dataframe
1. Use `create_epub.py` to convert those contents to an EPUB file and download, resize and convert all referenced images
1. Use the `EPUB-Checker.app` (freeware, download from https://www.pagina.gmbh/produkte/epub-checker/) to check the validity of your EPUB

## Cover
I Photoshopped a cover from the background and logo of the website into `cover.jpg`. Feel free to do the same

## Copyright
I don't store any copyrighted material here on GitHub, only the scripts I wrote to collect everything into an EPUB for personal use. All copyrights of all materials are with their respective authors
