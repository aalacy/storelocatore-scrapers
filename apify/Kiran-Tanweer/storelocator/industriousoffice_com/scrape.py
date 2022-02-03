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
        link_list = []
        search_url = "https://www.industriousoffice.com/locations"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        locations = soup.findAll("a", {"class": "gtm-all-locations-link"})
        for loc in locations:
            link = loc["href"]
            req = session.get(link, headers=headers)
            bs = BeautifulSoup(req.text, "html.parser")
            link = bs.findAll("a", {"class": "link-to-all gtm-view-details"})
            if link == []:
                url = loc["href"].strip()
                if loc["href"] not in link_list:
                    link_list.append(loc["href"])
            else:
                for url in link:
                    if url["href"] not in link_list:
                        link_list.append(url["href"])

        link = soup.findAll("a", {"class": "gtm-all-locations-international-link"})
        for loc_link in link:
            req = session.get(loc_link["href"], headers=headers)
            bs = BeautifulSoup(req.text, "html.parser")
            link = bs.findAll("a", {"class": "link-to-all gtm-view-details"})
            for loc in link:
                if link == []:
                    url = loc["href"].strip()
                    if loc["href"] not in link_list:
                        link_list.append(loc["href"])
                else:
                    for url in link:
                        if url["href"] not in link_list:
                            link_list.append(url["href"])

        for store in link_list:
            req = session.get(store, headers=headers)
            bs = BeautifulSoup(req.text, "html.parser")
            title = bs.find("h3", {"class": "location-name"}).text
            try:
                label = bs.find("div", {"data-test-id": "location_label"}).text
            except AttributeError:
                label = MISSING
            label = label.lower()
            if label.find("opening") != -1:
                title = title + " " + "Coming Soon"
            if label.find("coming") != -1:
                title = title + " " + "Coming Soon"
            phone = bs.find("a", {"class": "phone phone-ga-mobile"})
            if phone is None:
                phone = MISSING
            else:
                phone = phone.text
            address = bs.find("a", {"data-test-id": "location_address_link"}).text
            coords = bs.find("div", {"id": "locationMap"})
            lat = coords["data-lat"]
            lng = coords["data-lng"]
            if store.find("manchester") != -1:
                country = "UK"
            elif store.find("london") != -1:
                country = "UK"
            else:
                country = "US"
            address = address.strip()
            address = address.replace("\n", " ")
            address = address.replace("                     ", " ")

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

            if street == "Windmill Green 24 Mount St":
                pcode = state + " " + pcode
                state = MISSING

            if street == "245 Hammersmith Rd":
                pcode = state + " " + pcode
                state = MISSING
                city = "London"

            if street == "70 St Mary Axe London, Unit Ec3A 8Be":
                street = street.split("London")
                street, city = street
                pcode = city.split(",")
                pcode = pcode[1].strip()
                pcode = pcode.lstrip("Unit").strip()
                city = "London"
            title = title.strip()

            title = title.replace(
                "Industrious Biltmore Coming Soon", "Industrious Biltmore"
            ).strip()

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=store,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code=country,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
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
