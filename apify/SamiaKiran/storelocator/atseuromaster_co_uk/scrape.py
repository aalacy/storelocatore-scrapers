from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "atseuromaster_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.atseuromaster.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://centre.atseuromaster.co.uk/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.findAll(
            "div", {"class": "lf-footer-static__content__cities__list__wrapper"}
        )[-2].findAll("a")
        for state_url in statelist:
            url = "https://centre.atseuromaster.co.uk" + state_url["href"]
            state_url = state_url.get_text(separator="|", strip=True).replace("|", "")
            log.info(f"Fetching Locations from {state_url}")
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                page_list = (
                    soup.find("ul", {"class": "lf-pagination__list"})
                    .findAll("li")[-2]
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
            except:
                page_list = 1
            for page in range(1, int(page_list) + 1):
                url = (
                    "https://centre.atseuromaster.co.uk/gb/"
                    + state_url.lower()
                    + "?page="
                    + str(page)
                )
                r = session.get(url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                loclist = soup.findAll(
                    "a",
                    {
                        "class": "lf-geo-divisions__results__content__locations__list__item__name__link"
                    },
                )
                log.info(f"Fetching Locations from Page No {page}")
                for loc in loclist:
                    page_url = "https://centre.atseuromaster.co.uk" + loc["href"]
                    store_number = loc["href"].split("-")[0].replace("/", "")
                    log.info(page_url)
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    location_name = (
                        soup.find("h1")
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                    latitude = soup.find(
                        "meta", {"property": "place:location:latitude"}
                    )["content"]
                    longitude = soup.find(
                        "meta", {"property": "place:location:longitude"}
                    )["content"]
                    raw_address = (
                        soup.find("address")
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                    phone = soup.find(
                        "a", {"class": "lf-location-phone-default__phone"}
                    )["href"].replace("tel:", "")
                    hours_of_operation = (
                        soup.find("div", {"id": "lf-openinghours"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .replace("Show more Hide", "")
                    )
                    street_address = r.text.split('"streetAddress":"')[1].split('"')[0]
                    city = r.text.split('"addressLocality":"')[1].split('"')[0]
                    state = r.text.split('"addressRegion":"')[1].split('"')[0]
                    zip_postal = r.text.split('"postalCode":"')[1].split('"')[0]
                    country_code = "UK"
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
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
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
