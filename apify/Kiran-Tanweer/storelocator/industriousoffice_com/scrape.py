from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "industriousoffice_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.industriousoffice.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        locations = []
        diff_loc = []
        search_url = "https://www.industriousoffice.com/locations"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        US_locations = soup.find(
            "div", {"class": "all-locations-list row small-gutters"}
        ).findAll("a")
        for us_loc in US_locations:
            locations.append(us_loc["href"])
        Intl_locations = soup.findAll(
            "a", {"class": "gtm-all-locations-international-link"}
        )
        for intl_loc in Intl_locations:
            if intl_loc["href"].find("singapore") == -1:
                locations.append(intl_loc["href"])
        locations = list(dict.fromkeys(locations))
        for loc in locations:
            link = loc
            stores_req = session.get(link, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            try:
                title = soup.find("h3", {"class": "location-name"}).text
            except AttributeError:
                url = soup.findAll("a", {"class": "link-to-all gtm-view-details"})
                for loc_url in url:
                    locations.append(loc_url["href"])
        locations = list(dict.fromkeys(locations))
        for loc in locations:
            link = loc
            stores_req = session.get(link, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            store_type = link.split("com/")[1].split("/")[0].strip()
            if store_type == "m":
                store_type = "Market"
            else:
                store_type = "Industry"
            label = soup.find("div", {"data-test-id": "location_label"})
            if label is None:
                diff_loc.append(link)
                label = MISSING
                continue
            else:
                label = label.text
            try:
                title = soup.find("h3", {"class": "location-name"}).text
            except AttributeError:
                title = MISSING
            address = soup.find("address", {"class": "mb-0"}).find("a")
            coords = address["href"]
            address = address.text
            if label.find("Coming") != -1:
                title = title + " " + "Coming Soon"
            if label.find("Opening") != -1:
                title = title + " " + "Coming Soon"
            try:
                coords = coords.split("!3d")[1].strip()
                lat, lng = coords.split("!4d")
            except IndexError:
                try:
                    coords = coords.split("/@")[1].strip()
                    lat, lng = coords.split(",1")[0].split(",")
                except IndexError:
                    lat = MISSING
                    lng = MISSING
            try:
                phone = soup.find("a", {"class": "phone phone-ga-mobile"}).text
            except AttributeError:
                phone = MISSING

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
                store_number=MISSING,
                phone=phone,
                location_type=store_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=MISSING,
                raw_address=address,
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
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
