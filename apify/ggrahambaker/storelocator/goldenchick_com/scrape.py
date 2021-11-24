from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "goldenchick_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://goldenchick.com/"
MISSING = "<MISSING>"


def fetch_data():
    session = SgRequests()
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    url = "http://locations.goldenchick.com/"
    r = session.get(url, headers=HEADERS)

    soup = BeautifulSoup(r.content, "html.parser")

    loc_links = soup.find(
        "div", {"id": "parent_container_two"}
    ).previous_sibling.previous_sibling.find_all("a")

    state_list = []
    for loc in loc_links:
        state_list.append(loc)

    city_list = []
    for link in state_list:
        r = session.get(link["href"], headers=HEADERS)
        log.info(f"Fetching {link.text} Locations...")
        soup = BeautifulSoup(r.content, "html.parser")
        loc_links = soup.find(
            "div", {"id": "parent_container_two"}
        ).previous_sibling.previous_sibling.find_all("a")

        for loc in loc_links:
            if len(loc["href"].split("/")) == 6:
                city_list.append(loc)

    link_list = []
    for link in city_list:
        r = session.get(link["href"], headers=HEADERS, verify=False, timeout=150)
        log.info(f"Fetching {link.text} Locations...")
        soup = BeautifulSoup(r.content, "html.parser")
        loc_links = soup.find(
            "div", {"id": "parent_container_two"}
        ).previous_sibling.previous_sibling.find_all("a")

        for loc in loc_links:
            if len(loc["href"].split("/")) == 7:
                link_list.append(loc["href"])

    for link in link_list:
        r = session.get(link, headers=HEADERS)
        log.info(link)
        soup = BeautifulSoup(r.content, "html.parser")
        location_name = soup.find("meta", {"property": "og:title"})["content"]
        street_address = soup.find(
            "meta", {"property": "business:contact_data:street_address"}
        )["content"]
        city = soup.find("meta", {"property": "business:contact_data:locality"})[
            "content"
        ]
        state = soup.find("meta", {"property": "business:contact_data:region"})[
            "content"
        ]
        zip_postal = soup.find(
            "meta", {"property": "business:contact_data:postal_code"}
        )["content"]
        country_code = soup.find(
            "meta", {"property": "business:contact_data:country_name"}
        )["content"]
        phone = soup.find("meta", {"property": "business:contact_data:phone_number"})[
            "content"
        ]
        latitude = soup.find("meta", {"property": "place:location:latitude"})["content"]
        longitude = soup.find("meta", {"property": "place:location:longitude"})[
            "content"
        ]
        hours_divs = soup.find("div", {"id": "col_one"}).find_all("div")
        hours = ""
        for day in hours_divs:
            if "Holiday" in day.text:
                break
            hours += day.text.strip() + " "
        hours = " ".join(hours.split())
        store_number = link.split("/")[-2]
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=link,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
