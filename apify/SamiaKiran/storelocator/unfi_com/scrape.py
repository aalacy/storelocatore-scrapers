import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "unfi_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "cookie": "visid_incap_536781=kRXhn/08RI+24aoBO2PrKBsnGmAAAAAAQUIPAAAAAAAXVT4TPM5TbvN9NZq2aSCS; modal_shown=yes; _ga=GA1.2.599170801.1612326712; incap_ses_957_536781=BpfXGvxvizaG0Pg6qPJHDbIwHWAAAAAATgllZ2VtSVDKQe4kayxm8w==; has_js=1; nlbi_536781=suLlBE8elko3Mcps4PWBEQAAAACABHgqM+IzgoDi8/Yip48c; incap_ses_262_536781=ghhRcRqM22CNfB7W8s+iA80wHWAAAAAAQ9xXdcnCWsuspwCwOOZbvQ==; merger_modal=1; _gid=GA1.2.1653675809.1612525782",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    data = []
    url = "https://www.unfi.com/locations"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"markers":')[1].split(',"styleBubble":', 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        temp = loc["text"]
        soup = BeautifulSoup(temp, "html.parser")
        title = soup.find("strong").text
        lat = loc["latitude"]
        longt = loc["longitude"]
        street = soup.find("span", {"itemprop": "streetAddress"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        pcode = soup.find("span", {"class": "postal-code"}).text
        data.append(
            [
                "https://www.unfi.com/",
                "https://www.unfi.com/locations",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
