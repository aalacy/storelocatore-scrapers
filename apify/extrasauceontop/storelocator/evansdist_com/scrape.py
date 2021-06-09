from sgrequests import SgRequests
import PyPDF2  # noqa
import unidecode
from bs4 import BeautifulSoup as bs
import pandas as pd

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

requests = SgRequests()
url = "https://www.evansdist.com/detroit-warehousing/"
response = requests.get(url).text
soup = bs(response, "html.parser")

grids = soup.find_all("div", attrs={"class": "one-third"})
names = soup.find_all("div", attrs={"class": "two-thirds first"})

x = 0
for grid in grids:
    link = grid.find("a")["href"]
    if link.split(".")[-1] == "pdf":

        pdf_response = requests.get(link)
        my_raw_data = pdf_response.content

        with open("my_pdf.pdf", "wb") as my_data:
            my_data.write(my_raw_data)

        open_pdf_file = open("my_pdf.pdf", "rb")
        read_pdf = PyPDF2.PdfFileReader(open_pdf_file)

        final_text = unidecode.unidecode(read_pdf.getPage(0).extractText())

        locator_domain = "www.evansdist.com"
        page_url = link
        location_name = names[x].find("h3").text.strip()

        if "PROGRESSIVE DISTRIBUTION CENTERS" in final_text:
            address_parts = [
                item.strip()
                for item in final_text.split("PROGRESSIVE DISTRIBUTION CENTERS")[
                    1
                ].split("\n")
                if item != ""
            ]

        else:
            address_parts = [
                item.strip()
                for item in final_text.split("CENTRAL DETROIT WAREHOUSE")[1].split("\n")
                if item != ""
            ]

        address = address_parts[0]
        city = address_parts[1].split(",")[0]
        state = address_parts[1].split(", ")[1].split(" ")[0]
        zipp = address_parts[1].split(", ")[1].split(" ")[1]
        country_code = "US"

        store_number = "<MISSING>"
        phone = address_parts[2].strip().replace(".", "-")
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = "<MISSING>"

        locator_domains.append(locator_domain)
        page_urls.append(page_url)
        location_names.append(location_name)
        street_addresses.append(address)
        citys.append(city)
        states.append(state)
        zips.append(zipp)
        country_codes.append(country_code)
        store_numbers.append(store_number)
        phones.append(phone)
        location_types.append(location_type)
        latitudes.append(latitude)
        longitudes.append(longitude)
        hours_of_operations.append(hours)

        open_pdf_file.close()
        x = x + 1

df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_of_operations,
        "country_code": country_codes,
        "location_type": location_types,
    }
)

df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)
