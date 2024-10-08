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

search_query = """
<br><br><div class="h3">Company Description</div><br><br><div class="h3">Job Description</div><p><strong>About you:</strong></p><p>We are seeking a Machine Learning Engineer with over 3 years of experience to join our team. The successful candidate will specialize in collecting, processing, and analyzing textual data from various web sources to drive insights that inform business strategies.</p><p>You are someone who wants to influence your own development. You’re looking for a company where you have the opportunity to pursue your interests and be able to grow professionally.</p><p><strong>You bring to Applaudo the following competencies:</strong></p><ul style=""><li style="">Minimum +2 years of experience as a Machine Learning Engineer.</li><li style="">Strong programming skills in Python.</li><li style="">Experience with Cloud functions in GCP.</li><li style="">Experience using Dialogflow CX.</li><li style="">Proficient in using GCP and related GCP services for deploying and managing ML models.</li><li style="">Must: Expertise in applying RAG for enhancing model capabilities in real-time decision-making processes.</li><li style="">In-depth knowledge of data structures, data modeling, and software architecture.</li><li style="">Advanced understanding of mathematics, statistics, and algorithms.</li><li style="">Proven track record of working on NLP projects and applying natural language processing in a professional setting.</li><li style="">Advanced english level, as you'll be working directly with US clients.</li><li style="">Desirable: Strong foundation in MLOps practices, including automation of model lifecycle, continuous integration/continuous deployment (CI/CD) of ML models, and monitoring model performance.</li><li style="">Desirable: Highly-skilled in deploying tools like VCS (git) and collaboration (Docker and Kubernetes)</li><li style="">Desirable: Ability to work in Agile environments and proficiency with project management and collaboration tools.</li></ul><p><strong>You will be accountable for the following responsibilities:</strong></p><ul style=""><li style="">Design, develop and maintain conversation flows in Dialogflow CX.</li><li style="">Build and optimize complex conversation flows using Dialogflow CX.</li><li style="">Utilize advanced NLP techniques and ML frameworks to extract meaningful information and trends from textual data.</li><li style="">Implement and manage RAG and other relevant techniques, knowing when to apply each method for optimal results.</li><li style="">Collaborate with cross-functional teams to translate data insights into actionable business outcomes.</li><li style="">Design and maintain robust MLOps pipelines to streamline model training, deployment, and monitoring.</li></ul><br><br><div class="h3">Qualifications</div><br><br><div class="h3">Additional Information</div><div></div><p>Here at Applaudo Studios values as <strong>trust, communication, respect, excellence and team work</strong> are our keys to success. We know we are working with the best and thus treat each other with respect and admiration without asking.</p><p>Submit your application today, and don't miss this opportunity to join the Best Digital team in the Region!</p>
<p>We truly appreciate all the hard and outstanding work our team makes every day at Applaudo Studios, and that's why the perks that we offer, are deeply thought and designed as a way to thank them for their commitment and excellence.</p><p>Some of our perks and benefits:</p><ul style=""><li style="">Work from home</li><li style="">Flexible schedule</li><li style="">Celebrations</li><li style="">Special discounts</li><li style="">Entertainment area</li><li style="">Flexible work spaces</li><li style="">Great work environment</li><li style="">Private medical insurance</li></ul><p>*B<em>enefits may vary according to your location and/or availability. Request further information when applying.</em></p><img src="https://remotive.com/job/track/1932572/blank.gif?source=public_api" alt=""/>
"""
