from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import json
import re
from sgscrape import sgpostal as parser


session = SgRequests()
website = "industriousoffice_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {}

DOMAIN = "https://www.industriousoffice.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        cleanr = re.compile(r"<[^>]+>")
        search_url = "https://www.industriousoffice.com/locations"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        locations = soup.findAll("script", {"type": "text/javascript"})
        locations = str(locations[2])
        locations = locations.split("data for geolocation")[1].strip()
        locations = locations.split("</script>")[0].strip()
        locations = locations.split("var locationsCords =")
        us_locs = locations[1].rstrip(";").strip()
        us_locs = json.loads(us_locs)
        for loc in us_locs:
            link = loc["link"]
            if link.find("custom_locations") == -1:
                title = loc["title"]
                lat = loc["lat"]
                lng = loc["lng"]
                store_id = loc["id"]
                stores_req = session.get(link, headers=headers)
                soup = BeautifulSoup(stores_req.text, "html.parser")
                try:
                    address = soup.find("address", {"class": "mb-0"}).find("a")
                    address = str(address)
                    address = address.split('"_blank">')[1].split("</a>")[0].strip()
                    address = address.replace("<br/>", " ")
                except AttributeError:
                    address = soup.find("span", {"class": "ml-1 font-weight-bold"}).text
                try:
                    phone = soup.find("a", {"class": "phone phone-ga-mobile"}).text
                except AttributeError:
                    phone = MISSING
                try:
                    label = soup.find("div", {"data-test-id": "location_label"}).text
                except AttributeError:
                    label = MISSING

                if label.find("open") != -1:
                    title = title + " " + "Coming Soon"
                if label.find("coming") != -1:
                    title = title + " " + "Coming Soon"

                if address.find("|") != -1:
                    raw_ad = address.split("|")
                    if raw_ad[0].find("Mon") != -1:
                        hours = raw_ad[0]
                        address = raw_ad[1]
                    elif raw_ad[1].find("Mon") != -1:
                        hours = raw_ad[1]
                        address = raw_ad[0]
                    elif raw_ad[0].find("Industrious") != -1:
                        address = raw_ad[1]
                    else:
                        hours = MISSING
                else:
                    hours = MISSING
                address = re.sub(pattern, " ", address)
                address = re.sub(cleanr, " ", address)

                address = address.replace(",", "")
                address = address.strip()
                parsed = parser.parse_address_usa(address)
                street1 = (
                    parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
                )
                street = (
                    (street1 + ", " + parsed.street_address_2)
                    if parsed.street_address_2
                    else street1
                )
                city = parsed.city if parsed.city else "<MISSING>"
                state = parsed.state if parsed.state else "<MISSING>"
                pcode = parsed.postcode if parsed.postcode else "<MISSING>"

                if link.find("london") != -1:
                    country = "UK"
                elif link.find("manchester") != -1:
                    country = "UK"
                else:
                    country = "US"

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code=country,
                    store_number=store_id,
                    phone=phone,
                    location_type=MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                    raw_address=address,
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.STORE_NUMBER})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
