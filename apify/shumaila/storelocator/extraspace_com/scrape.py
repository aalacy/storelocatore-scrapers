import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "extraspace.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://extraspace.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.find(
            "div", {"data-qa-footer-menu": "self-storage-locations"}
        ).findAll("a")
        for state_url in statelist:
            log.info(f"Fetching locations from state {state_url.text} ...")
            r = session.get(state_url["href"], headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("a", {"class": "secondary-link"})
            for loc in loclist:
                page_url = DOMAIN + loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                if r.status_code == 200:
                    content = r.text.split(
                        '<script id="JsonLdSelfStorageScript" type="application/ld+json">',
                        1,
                    )[1].split("</script>")[0]
                    content = json.loads(content)
                    city = content["address"]["addressLocality"]
                    state = content["address"]["addressRegion"]
                    zip_postal = content["address"]["postalCode"]
                    street_address = content["address"]["streetAddress"].replace(
                        "<br />", " "
                    )
                    location_name = content["name"].replace("?", "")
                    phone = content["telephone"].replace("+1-", "")
                    latitude = content["geo"]["latitude"]
                    longitude = content["geo"]["longitude"]
                    store_number = page_url.split("/")[-2]
                    soup = BeautifulSoup(r.text, "html.parser")
                    hours_of_operation = (
                        soup.find("div", {"class": "office-column"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .replace("Office Hours", "")
                    )
                    country_code = "US"
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
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
