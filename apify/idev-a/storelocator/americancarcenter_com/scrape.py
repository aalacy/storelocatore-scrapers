from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("americancarcenter")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.americancarcenter.com"
base_url = "https://www.americancarcenter.com/locations-at-american-car-center"


def _fetch(soup, store_number, page_url, hours=[]):
    sp1 = bs(
        soup.select_one("a.header-contact__link.js-location")["data-content"],
        "lxml",
    )
    markers = sp1.img["data-src"].split("&markers=size:small|")[1:]
    locations = sp1.select("div.get-direction__dealer")
    for x, _ in enumerate(locations):
        raw_address = (
            _.select_one("div.get-direction__dealer-name")
            .find_next_sibling()
            .text.strip()
        )
        addr = raw_address.split(",")
        try:
            phone = (
                _.select_one("div.get-direction__dealer-name")
                .find_next_sibling()
                .find_next_sibling()
                .text.strip()
            )
        except:
            phone = ""
        marker = markers[x].split("%2C")
        if store_number == _["data-id"]:
            return SgRecord(
                page_url=page_url,
                store_number=_["data-id"],
                location_name=_.select_one(
                    "div.get-direction__dealer-name"
                ).text.strip(),
                street_address=addr[0],
                city=addr[1].strip(),
                state=addr[-1].split()[0].strip(),
                zip_postal=addr[-1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=marker[0],
                longitude=marker[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("main.js-layout-main-block div.container p a")
        for loc in locations:
            page_url = locator_domain + loc["href"].replace(" ", "-")
            try:
                store_number = page_url.split("location-")[1].split("-")[0]
            except:
                store_number = page_url.split("dealerId=")[1].split("&")[0]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            hours = []
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                hours = [
                    " ".join(hh.stripped_strings)
                    for hh in sp1.select("div.widget-paragraph table tr")
                ]
                try:
                    ss = json.loads(
                        sp1.find_all("script", type="application/ld+json")[-1].string
                    )["offers"][0]["seller"]
                    addr = ss["address"]
                    yield SgRecord(
                        page_url=page_url,
                        store_number=store_number,
                        location_name=ss["name"],
                        street_address=addr["streetAddress"],
                        city=addr["addressLocality"],
                        state=addr["addressRegion"],
                        zip_postal=addr["postalCode"],
                        country_code="US",
                        phone=ss["telephone"],
                        latitude=ss["geo"]["latitude"],
                        longitude=ss["geo"]["longitude"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )
                except:
                    yield _fetch(soup, store_number, page_url, hours)
            else:
                yield _fetch(soup, store_number, page_url)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
