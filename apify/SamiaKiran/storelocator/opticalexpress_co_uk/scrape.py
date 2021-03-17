import csv
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "opticalexpress_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
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
    final_data = []
    temp = []
    if True:
        locator_domain = "https://www.opticalexpress.co.uk/clinic-finder"
        r = session.get(locator_domain, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "clinics-grid__item inline-block"})
        for loc in loclist:
            page_url = loc.find("a")["href"]
            page_url = "https://www.opticalexpress.co.uk/" + page_url
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            raw_address = soup.find("p", {"class": "clinic__address"}).get_text(
                separator=",", strip=True
            )
            if raw_address in temp:
                continue
            temp.append(raw_address)
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address is None:
                street_address = formatted_addr.street_address_2
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = formatted_addr.city
            state = formatted_addr.state if formatted_addr.state else "<MISSING>"
            zip_postal = formatted_addr.postcode
            country_code = "GB"
            location_name = soup.find("h1").text
            try:
                phone = soup.findAll("div", {"class": "contact-information"})[1]
                phone = phone.find("a").text
            except:
                phone = soup.findAll("div", {"class": "contact-information"})[0]
                phone = phone.find("a").text
            hour_list = soup.find("ul", {"class": "opening-times"}).findAll("li")
            hours_of_operation = ""
            for hour in hour_list:
                day = hour.find("span", {"class": "opening-times__day"}).text.strip()
                time = hour.find("div", {"class": "opening-times__hours"}).text.strip()
                hours_of_operation = hours_of_operation + " " + day + " " + time
            log.info(page_url)

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
