from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup, Tag
import json
from ncls_formatter import ncls_formatter

def extract_bold(soup: BeautifulSoup, label: str) -> str | None:
    """
    Finds a <b> tag with a given label and extracts all subsequent text
    content until a <br> tag is encountered.
    """
    bold_tag = soup.find("b", string=lambda t: t and t.strip().startswith(label))
    if not bold_tag:
        return None
    
    content = []
    # Loop through the nodes immediately following the <b> tag
    for sibling in bold_tag.next_siblings:
        # Stop when we hit the line break for the next field
        if sibling.name == 'br':
            break
        
        # If the sibling is another tag (like an <a>), get its text
        if isinstance(sibling, Tag):
            content.append(sibling.get_text(strip=True))
        # If it's a NavigableString (just text), strip and add it
        else:
            content.append(str(sibling).strip())
            
    # Join the collected parts and clean up
    full_text = " ".join(filter(None, content))
    return full_text if full_text else None


def scrape_bills(page: Page) -> list:
    bills_data = []
    
    # 1. Get the HTML of the entire results container for robust parsing
    results_container_html = page.locator('#dnn_ctr15755_StateNetDB_linkList').inner_html()
    
    # 2. Parse the entire block with BeautifulSoup
    soup = BeautifulSoup(results_container_html, "html.parser")

    # 3. Find all bill headers, which act as starting points for each bill
    bill_headers = soup.find_all("div", class_="h2Headers1")

    for header in bill_headers:
        # 4. Collect all HTML tags belonging to a single bill.
        # A bill's content starts at a header and ends before the next header or <hr>.
        bill_tags = [header]
        for sibling in header.find_next_siblings():
            # Stop if we've reached the next bill's header
            if sibling.name == 'div' and 'h2Headers1' in sibling.get('class', []):
                break
            # Or stop if we've reached the separator between bills
            if sibling.name == 'hr':
                break
            bill_tags.append(sibling)

        # 5. Create a new, isolated soup object for just this bill's complete HTML
        bill_html = "".join(str(t) for t in bill_tags)
        bill_soup = BeautifulSoup(bill_html, "html.parser")

        # 6. Extract fields using the complete and isolated bill HTML
        state = bill_soup.find("div", class_="h2Headers1").get_text(strip=True)

        bill_link_tag = bill_soup.find("a")
        bill_number = bill_link_tag.get_text(strip=True) if bill_link_tag else None
        bill_url = bill_link_tag['href'] if bill_link_tag else None

        # The year is reliably found after the bill link and a <br> tag
        year = None
        if bill_link_tag and bill_link_tag.find_next_sibling('br'):
            year_node = bill_link_tag.find_next_sibling('br').next_sibling
            if year_node:
                year = year_node.strip()

        subject_div = bill_soup.find("div", style="font-weight: bold;")
        subject_text = subject_div.get_text(strip=True) if subject_div else None

        # Use the improved helper function to reliably extract data
        bills_data.append({
            "state": state,
            "bill_number": bill_number,
            "bill_url": bill_url,
            "year": year,
            "subject": subject_text,
            "status": extract_bold(bill_soup, "Status:"),
            "date_last_action": extract_bold(bill_soup, "Date of Last Action:"),
            "author_info": extract_bold(bill_soup, "Author:"),
            "topics": extract_bold(bill_soup, "Topics:"),
            "associated_bills": extract_bold(bill_soup, "Associated Bills:"),
            "summary": extract_bold(bill_soup, "Summary:")
        })

    return bills_data

def save_bills_to_json(page, filename: str):
    """
    Saves the list of bills data to a JSON file.
    """
    ndjson_data = scrape_bills(page)

    # Write NDJSON
    with open("data/{filename}", "w", encoding="utf-8") as f:
        for line in ndjson_data:
            f.write(json.dumps(line) + "\n")

    print(f"✅ Scraped {len(ndjson_data)} bills. Saved to {filename}.")

def scrape_ncsl():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to NCSL Public Health Legislation Database...")
        page.goto("https://www.ncsl.org/health/state-public-health-legislation-database", timeout=60000)

        # Select "All Topics"
        print("Selecting 'All Topics'...")
        page.get_by_label("All Topics").click()

        # Select "All States"
        print("Selecting 'All States'...")
        page.get_by_label("All States").click()

        # Select keyword "Surveillance"
        print("Selecting keyword 'Surveillance'...")
        # Using Locator with the ID of the input field because it does not have a label
        page.locator('#dnn_ctr15755_StateNetDB_txtKeyword').fill("Surveillance")

        # Click "Search"
        print("Submitting search...")
        # Using Locator with the ID of the Search button because it does not have a label
        page.locator('#dnn_ctr15755_StateNetDB_btnSearch').click()

        # Wait for results table
        print("Waiting for results...")
        results_container = page.locator("#dnn_ctr15755_StateNetDB_linkList")

        # Wait for content to be non-empty
        # Wait until the page contains an element inside the #dnn_ctr15755_StateNetDB_linkList container includes the visible text "Summary:".
        page.wait_for_selector("#dnn_ctr15755_StateNetDB_linkList >> text=Summary:")

        # Select all bill blocks
        bill_blocks = page.locator('xpath=//div[@id="dnn_ctr15755_StateNetDB_linkList"]')
        
        # Extract inner HTML of the div
        html_content = page.eval_on_selector(
            "#dnn_ctr15755_StateNetDB_linkList", "el => el.innerHTML"
        )

        print(html_content)

        formatter = ncls_formatter(is_mock=True)
        html_table = formatter.format_as_html_table(html_content)
        print("Generated HTML Table:")
        print(html_table)

        browser.close()

if __name__ == "__main__":
    scrape_ncsl()