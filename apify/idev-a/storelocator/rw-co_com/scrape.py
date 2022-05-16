from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("rw-co")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.rw-co.com/"
base_url = "https://locations.rw-co.com/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('"FeatureCollection","features":')[1]
            .split('},"uiLocationsList"')[0]
            .strip()
        )
        for _ in locations:
            page_url = base_url + _["properties"]["slug"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            try:
                ss = json.loads(sp1.find("script", type="application/ld+json").string)
            except:
                continue
            hours = [
                f"{hh['dayOfWeek']}: {hh['opens']}-{hh['closes']}"
                for hh in ss["openingHoursSpecification"]
            ]
            yield SgRecord(
                page_url=page_url,
                store_number=_["properties"]["id"],
                location_name=_["properties"]["name"],
                street_address=sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
                state=sp1.select_one('span[itemprop="addressRegion"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                country_code=ss["address"]["addressCountry"],
                phone=ss["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
