from playwright.sync_api import sync_playwright
import json
import re

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

        elements = results_container.locator("xpath=./*")
        count = elements.count()

        ndjson_lines = []
        current_state = None

        for i in range(count):
            el = elements.nth(i)
            tag = el.evaluate("e => e.tagName")

            if tag == "DIV":
                class_attr = el.get_attribute("class") or ""

                # Detect state header
                if "h2Headers1" in class_attr:
                    current_state = el.inner_text().strip().split("\n")[0]

                # Detect bill div (no class, contains bill link)
                elif class_attr == "":
                    anchor = el.locator("a")
                    if anchor.count() > 0:
                        bill_number = anchor.inner_text().strip()
                        year = el.inner_text().strip().split("\n")[-1].strip()
                        bill_url = anchor.get_attribute("href").strip()
                        
                        # Look ahead to grab metadata in following sibling divs
                        status = ""
                        date = ""
                        sponsor = ""
                        summary = ""

                        # Check next few siblings
                        for j in range(1, 6):
                            if i + j >= count:
                                break

                            next_el = elements.nth(i + j)
                            text = next_el.inner_text().strip()

                            if text.startswith("Status:"):
                                status = text.replace("Status:", "").strip()
                            elif text.startswith("Date of Last Action:"):
                                date = text.replace("Date of Last Action:", "").strip()
                            elif text.startswith("Author:"):
                                match = re.search(r"Author:\s*(.+?)(?:Additional Authors:|Topics:|$)", text)
                                if match:
                                    sponsor = match.group(1).strip()
                            elif text.startswith("Summary:"):
                                summary = text.replace("Summary:", "").strip()

                        ndjson_lines.append({
                            "State": current_state,
                            "BillNumber": bill_number,
                            "Status": status,
                            "Date": date,
                            "Sponsor": sponsor,
                            "Summary": summary,
                            "URL": bill_url,
                            "Year": year
                        })

        # Write NDJSON
        with open("data/surveillance_bills.ndjson", "w", encoding="utf-8") as f:
            for line in ndjson_lines:
                f.write(json.dumps(line) + "\n")

        print(f"✅ Scraped {len(ndjson_lines)} bills. Saved to surveillance_bills.ndjson.")

        browser.close()

if __name__ == "__main__":
    scrape_ncsl()