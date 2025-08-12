# app/services/ncls_formatter.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Load the API key from environment variable
client = OpenAI(
  api_key=os.environ["API_KEY"]
)


class ncls_formatter:
    def __init__(self, is_mock: bool = False, model: str = "gpt-4o", max_tokens: int = 1000):
        self.is_mock = is_mock
        self.model = model
        self.max_tokens = max_tokens

    def format_as_html_table(self, results: str) -> str:
        """
        Summarizes a single piece of legislation using OpenAI.
        Expects bill_data to include keys like 'State', 'BillNumber', and 'Summary'.
        Returns a short summary string.
        """
        if self.is_mock:
            # Read and return the content of the mock HTML file
            try:
                # Use a path relative to the script's location
                script_dir = os.path.dirname(__file__)
                file_path = os.path.join(script_dir, "mock_table.html")
                with open(file_path, "r") as file:
                    return file.read()
            except FileNotFoundError:
                return "<p>Error: mock_table.html not found.</p>"
        else:
            # Prepare the prompt for the OpenAI API
            prompt = self._build_ncls_table_prompt(results)

            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=0.5,
                )

                html_table = response['choices'][0]['message']['content'].strip()
                return html_table

            except Exception as e:
                print(f"[Summarizer Error] {e}")
                return "Summary could not be generated."

        def _build_ncls_table_prompt(self, ncls_results: str) -> str:
            return f"""
    You are helping format the results from a web search for legislative bills into an HTML table that lists each bill in a single row. The table must include the following columns: State, Bill Number, Bill Link, Year, Focus, Status, Date of Last Action, Author, Additional Authors, Topics, Associated Bills, Summary.

    BEGIN SAMPLE INPUT
    <div id="dnn_ctr15755_StateNetDB_linkList" style="width: 99%; text-align: left; margin-top: 10px">
        
                <div class='h2Headers1'>Hawaii<div style='float: right; padding-right: 5px;'></div></div>
                <div style="clear: both">
                </div>
                <div>
                    <a href='http://custom.statenet.com/public/resources.cgi?id=ID:bill:HI2025000HCR145&ciq=ncsl&client_md=c1bb9c14cf27de35f85a1a8c4f520da7&mode=current_text' target='_blank'>HI HCR  145</a><br />
                    2025<br />
                </div>
                <div style="font-weight: bold;">
                    Autism Spectrum Disorder<br />
                </div>
                <b>Status:</b>
                Failed - Adjourned - In Multiple Committees
                <br />
                <b>Date of Last Action:</b>
                3/7/2025
                <br />
                <b>Author:</b>
                Kapela (D)<b> Additional Authors: </b>Perruso (D);Marten (D);Amato (D);Kila (D);Shimizu (R)
                <br />
                <b>Topics: </b>
                Health Disparities
                <br />
                <b>Associated Bills: </b>HI HR 139 - Companion<br/>
                <b>Summary: </b>
                Urges the Department of Education, Department of Health, and other relevant stakeholders to collaborate and develop a strategic plan to prepare for the state's pursuit of funding for and participation in the centers for disease control and prevention's public health surveillance for estimating autism prevalence.
                <br />
                <div id="divClickforHistory">
                    <b>History:</b> <a href="#" role="button" class="clickForHistory">Click for History</a><br />
                </div>
                <div id="dnn_ctr15755_StateNetDB_repResults_divHistoryList_0" class="historyList" style="display: none">
                    03/07/2025 - INTRODUCED.<br/>03/14/2025 - To HOUSE Committee on EDUCATION.<br/>03/14/2025 - Subsequent referral set for: HOUSE Committee on HEALTH.<br/>03/18/2025 - In Committee: Hearing Scheduled.<br/>03/20/2025 - In HOUSE Committee on EDUCATION:  Voted do pass.<br/>03/25/2025 - From HOUSE Committee on EDUCATION:  Do pass.<br/>03/25/2025 - To HOUSE Committee on HEALTH.<br/>03/28/2025 - In Committee: Hearing Scheduled.<br/>04/02/2025 - In HOUSE Committee on HEALTH:  Voted do pass.<br/>04/03/2025 - From HOUSE Committee on HEALTH:  Do pass.<br/>04/03/2025 - In HOUSE.  Read third time.  Passed HOUSE.  *****To SENATE.<br/>04/04/2025 - To SENATE Committee on EDUCATION.<br/>04/04/2025 - Additionally referred to SENATE Committee on HEALTH AND HUMAN SERVICES.
                </div>
                <br />
                
    </div>
    END SAMPLE INPUT

    BEGIN SAMPLE OUTPUT
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sample HTML Table</title>
    </head>
    <body>
        <h1 style="text-align: center;">Sample Table</h1>
        <table>
            <thead>
                <tr>
                    <th>State</th>
                    <th>Bill Number</th>
                    <th>Bill Link</th>
                    <th>Year</th>
                    <th>Focus</th>
                    <th>Status</th>
                    <th>Date of Last Action</th>
                    <th>Author</th>
                    <th>Additional Authors</th>
                    <th>Topics</th>
                    <th>Associated Bills</th>
                    <th>Summary</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Hawaii</td>
                    <td>HI HCR  145</td>
                    <td>http://custom.statenet.com/public/resources.cgi?id=ID:bill:HI2025000HCR145&ciq=ncsl&client_md=c1bb9c14cf27de35f85a1a8c4f520da7&mode=current_text</td>
                    <td>2025</td>
                    <td>Autism Spectrum Disorder</td>
                    <td>Failed - Adjourned - In Multiple Committees</td>
                    <td>3/7/2025</td>
                    <td>Kapela (D)</td>
                    <td>Perruso (D);Marten (D);Amato (D);Kila (D);Shimizu (R)</td>
                    <td>Health Disparities</td>
                    <td>HI HR 139 - Companion</td>
                    <td>Urges the Department of Education, Department of Health, and other relevant stakeholders to collaborate and develop a strategic plan to prepare for the state's pursuit of funding for and participation in the centers for disease control and prevention's public health surveillance for estimating autism prevalence.</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    END SAMPLE OUTPUT

    BEGIN RESULTS
    {ncls_results}
    END RESULTS
    """
