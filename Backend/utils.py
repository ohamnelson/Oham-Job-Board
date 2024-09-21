import re
from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert


def normalize_salary(salary):
    # Step 1: Remove any extra text
    salary = salary.lower()
    salary = re.sub(r'(plus.*|competitive.*|equity.*|stock.*|bonus.*|dependent.*|options.*|salary.*|remuneration.*|pre-ipo.*|commission.*|packages.*|bonus.*)', '', salary)
    
    # Step 2: Normalize ranges by converting various types of separators to '-'
    salary = salary.replace('to', '-').replace('–', '-').replace('—', '-').replace('–', '-')
    
    # Step 3: Handle 'k' notation (e.g., '50k' -> '50000')
    salary = re.sub(r'(\d+)k', lambda x: str(int(x.group(1)) * 1000), salary)
    
    # Step 4: Convert monthly and hourly rates to annual (assuming 12 months per year for monthly and 2080 hours per year for hourly)
    if 'hour' in salary:
        match = re.search(r'(\d+)-(\d+) (\$|\£|\€)? per hour', salary)
        if match:
            low, high = int(match.group(1)), int(match.group(2))
            salary = f'{int(((low + high) / 2) * 2080)}'
    
    if 'month' in salary:
        match = re.search(r'(\d+)-(\d+) (\$|\£|\€)? per month', salary)
        if match:
            low, high = int(match.group(1)), int(match.group(2))
            salary = f'{int(((low + high) / 2) * 12)}'
    
    # Step 5: Handle different currencies
    # For simplicity, let's assume all values are in USD or can be compared directly
    # salary = re.sub(r'[€£]', '$', salary)  # Convert other currencies to USD symbol
    
    # Step 6: Remove unwanted text such as '/year', etc.
    salary = re.sub(r'(per.*|/.*)', '', salary)
    
    # Step 7: Extract and format numeric values
    match = re.search(r'(\d+(?:,\d{3})*)', salary)
    if match:
        salary = f'{match.group(1).replace(",", "")}'
    else:
        salary = '0'  # Default value if nothing matched

    return salary


def clean_html(html_content):
    """
    Cleans up HTML content by removing non-breaking spaces, unnecessary inline styles,
    and ensuring proper tag formatting.

    Parameters:
    html_content (str): The HTML content to clean.

    Returns:
    str: The cleaned HTML content.
    """
    if not html_content:
        return ''
    
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove empty paragraphs, spaces, and other unwanted content
    for tag in soup.find_all():
        # Remove unwanted inline styles and attributes
        tag.attrs = {}
        
        # Remove empty tags (if they contain no meaningful text or children)
        if tag.name == 'p' and (not tag.text.strip() or tag.text == '\xa0'):
            tag.decompose()

    # Clean up multiple newlines or unnecessary tags
    cleaned_html = str(soup).replace('\n', '').replace('\xa0', ' ').strip()

    return cleaned_html

def decode_unicode_escape(input_str):
    # Define a function to convert \uXXXX to the actual character
    def unicode_escape_to_char(match):
        hex_value = match.group(1)
        return chr(int(hex_value, 16))
    
    # Replace all \uXXXX with the actual character
    decoded_str = re.sub(r'\\u([0-9A-Fa-f]{4})', unicode_escape_to_char, input_str)
    
    return decoded_str

def insert_on_conflict_nothing(table, conn, keys, data_iter):
    # "a" is the primary key in "conflict_table"
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data).on_conflict_do_nothing(index_elements=["Id"])
    result = conn.execute(stmt)
    return result.rowcount