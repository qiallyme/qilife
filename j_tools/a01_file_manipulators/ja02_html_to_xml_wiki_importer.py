import os
import glob
import time
import html2text
from lxml import etree
from datetime import datetime

# Configuration
XML_FILE_PATH = r'C:\Users\Cody\Downloads\iisitax_Jan-24-2025\index.xml'  # Path to your existing XML file
HTML_FILES_DIRECTORY = r'C:\Users\Cody\Downloads\wiki'  # Directory containing HTML files
OUTPUT_XML_FILE = r'C:\Users\Cody\Downloads'  # Path for the updated XML
AUTHOR_ID = 'un159522404389453887r84id'  # Replace with your actual author ID
TYPE = '0'  # Assuming '0' is the standard page type
VERSION = '1.0'  # Starting version for new pages

def parse_existing_xml(xml_path):
    """Parse the existing XML and return the tree and root."""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_path, parser)
    root = tree.getroot()
    return tree, root

def get_current_max_id(root):
    """Find the maximum current ID in <page> elements to generate new unique IDs."""
    ids = root.xpath('.//pages/page/id/text()')
    numeric_ids = [int(id_) for id_ in ids if id_.isdigit()]
    return max(numeric_ids) if numeric_ids else 0

def convert_html_to_cdata(html_content):
    """Convert HTML content to CDATA section."""
    return etree.CDATA(html_content)

def generate_timestamp():
    """Generate current timestamp in milliseconds."""
    return str(int(time.time() * 1000))

def derive_page_name_and_url(file_name):
    """Derive the page name and URL from the HTML file name."""
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    # Replace underscores and hyphens with spaces for the page name
    page_name = base_name.replace('_', ' ').replace('-', ' ').title()
    # For URL, you might want to keep it URL-friendly (e.g., use hyphens)
    page_url = base_name.replace(' ', '-')
    return page_name, page_url

def add_page(root, new_id, page_name, page_url, html_content):
    """Create a new <page> element and append it to <pages>."""
    pages_element = root.find('pages')
    if pages_element is None:
        print("No <pages> element found in XML.")
        return

    page = etree.SubElement(pages_element, 'page')

    # <id>
    id_el = etree.SubElement(page, 'id')
    id_el.text = str(new_id)

    # <name>
    name_el = etree.SubElement(page, 'name')
    name_el.text = etree.CDATA(page_name)

    # <url>
    url_el = etree.SubElement(page, 'url')
    url_el.text = page_url

    # <type>
    type_el = etree.SubElement(page, 'type')
    type_el.text = TYPE

    # <author>
    author_el = etree.SubElement(page, 'author')
    author_el.text = AUTHOR_ID

    # <version>
    version_el = etree.SubElement(page, 'version')
    version_el.text = VERSION

    # <createdon>
    createdon_el = etree.SubElement(page, 'createdon')
    createdon_el.text = generate_timestamp()

    # <modifiedby>
    modifiedby_el = etree.SubElement(page, 'modifiedby')
    modifiedby_el.text = AUTHOR_ID

    # <modifiedon>
    modifiedon_el = etree.SubElement(page, 'modifiedon')
    modifiedon_el.text = generate_timestamp()

    # <content>
    content_el = etree.SubElement(page, 'content')
    content_el.text = etree.CDATA(html_content)

    # <pageattachments> (empty for now; can be populated if needed)
    pageattachments_el = etree.SubElement(page, 'pageattachments')
    # If you have attachments to add, populate this section accordingly

def process_html_files(tree, root):
    """Process all HTML files and add them as new pages."""
    html_files = glob.glob(os.path.join(HTML_FILES_DIRECTORY, '*.html'))
    print(f'Found {len(html_files)} HTML files to process.')

    current_max_id = get_current_max_id(root)
    print(f'Current maximum ID: {current_max_id}')

    for idx, html_file in enumerate(html_files, start=1):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Optionally, convert HTML to plain text or another format if needed
        # For now, we'll embed the HTML directly
        # If conversion is needed:
        # converter = html2text.HTML2Text()
        # converter.ignore_links = False
        # wiki_text = converter.handle(html_content)
        # Use 'wiki_text' instead of 'html_content' if conversion is done

        page_name, page_url = derive_page_name_and_url(html_file)
        new_id = current_max_id + idx

        print(f'Adding page: {page_name} with ID: {new_id}')

        add_page(root, new_id, page_name, page_url, html_content)

def main():
    # Parse the existing XML
    tree, root = parse_existing_xml(XML_FILE_PATH)

    # Process HTML files and add them to the XML
    process_html_files(tree, root)

    # Write the updated XML to the output file
    tree.write(OUTPUT_XML_FILE, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    print(f'Updated XML written to {OUTPUT_XML_FILE}')

if __name__ == '__main__':
    main()
