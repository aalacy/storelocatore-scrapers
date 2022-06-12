from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.goddessandthebaker.com"
base_url = "https://www.goddessandthebaker.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one('script[type="application/ld+json"]')
            .text
        )["subOrganization"]
        for _ in locations:
            page_url = _["url"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in sp1.select("section#intro p")[1:]:
                hr = hh.text.strip()
                if "Order" in hr or "Pick" in hr or "Park" in hr or "upstairs" in hr:
                    break
                if "downstairs" in hr:
                    continue
                hours.append(hr)
            addr = _["address"]
            latlng = sp1.select_one("div.gmaps")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=addr["streetAddress"],
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=addr["postalCode"],
                latitude=latlng["data-gmaps-lat"],
                longitude=latlng["data-gmaps-lng"],
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(
                    sp1.select_one(
                        'a[data-bb-track-category="Address"]'
                    ).stripped_strings
                ),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
