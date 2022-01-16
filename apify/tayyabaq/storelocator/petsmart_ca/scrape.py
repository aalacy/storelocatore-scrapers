import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "petsmart_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://petsmart.ca/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.petsmart.ca/stores/ca/"
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    store = soup.find("div", class_="all-states-list container")
    str = store.find_all("a")
    for i in str:
        newurl = i["href"]
        log.info(f"Fetching locations for state {i.text}")
        page = session.get(newurl, headers=headers)
        if page.status_code != 200:
            continue
        soup = BeautifulSoup(page.content, "html.parser")
        store = soup.find_all("a", class_="store-details-link")
        for j in store:
            page_url = newurl + j["href"]
            log.info(page_url)
            if "closed" in page_url.lower():
                continue
            page = session.get(page_url, headers=headers)
            if page.status_code != 200:
                continue
            soup = BeautifulSoup(page.content, "html.parser")
            div = soup.find("div", class_="store-page-details")
            try:
                location_name = div.find("h1").text
                if "closed" in location_name.lower():
                    continue
            except:
                continue
            phone = div.find("p", class_="store-page-details-phone").text.strip()
            addr = (
                div.find("p", class_="store-page-details-address")
                .text.strip()
                .split("\n")
            )
            if len(addr) == 2:
                street = addr[0]
                addr = addr[1].strip().split(",")
            elif len(addr) > 2:
                add = addr[-1]
                del addr[-1]
                street = " ".join(addr)
                addr = add.strip().split(",")

            city = addr[0]
            addr = addr[1].strip().split(" ")
            state = addr[0]
            del addr[0]
            zip_postal = " ".join(addr).strip()
            try:
                hours = soup.find(
                    "div",
                    class_="store-page-details-hours-mobile visible-sm visible-md ui-accordion ui-widget ui-helper-reset",
                ).text
            except:
                try:
                    hours = soup.find(
                        "div",
                        class_="store-page-details-hours-mobile visible-sm visible-md",
                    ).text
                except:
                    hours = MISSING
            hours = hours.strip().replace("\n\n", "").replace("\n", "")
            for day in ["MON", "TUE", "THU", "WED", "FRI", "SAT", "SUN"]:
                if day not in hours:
                    hours = hours.replace("TODAY", day)
            lat, long = re.findall(
                r"center=([\d\.]+),([\-\d\.]+)",
                soup.find("div", class_="store-page-map mapViewstoredetail")
                .find("img")
                .get("src"),
            )[0]
            country_code = "CA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=lat,
                longitude=long,
                hours_of_operation=hours,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
