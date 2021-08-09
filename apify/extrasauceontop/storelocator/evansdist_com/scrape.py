from sgrequests import SgRequests
import PyPDF2  # noqa
import unidecode
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp

requests = SgRequests()
url = "https://www.evansdist.com/detroit-warehousing/"
response = requests.get(url).text
soup = bs(response, "html.parser")

buttons = soup.find_all("div", attrs={"class": "elementor-button-wrapper"})
names = soup.find_all("h3", attrs={"class": "elementor-image-box-title"})

for button in buttons:
    if "upload" in button.find("a")["href"] and "Company-Overview" not in button.find("a")["href"]:
        print(button.find("a")["href"])

# pdf_response = requests.get(link)
# my_raw_data = pdf_response.content

# with open("my_pdf.pdf", "wb") as my_data:
#     my_data.write(my_raw_data)

# open_pdf_file = open("my_pdf.pdf", "rb")
# read_pdf = PyPDF2.PdfFileReader(open_pdf_file)

# final_text = unidecode.unidecode(read_pdf.getPage(0).extractText())

# with open("file.txt", "w", encoding="utf-8") as output:
#     print(final_text, file=output)






