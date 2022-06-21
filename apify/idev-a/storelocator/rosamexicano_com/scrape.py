from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from lxml import html
import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rosamexicano")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.rosamexicano.com/"
base_url = "https://www.rosamexicano.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("script", type="application/ld+json")
            .string.strip()
        )
        for _ in locations["subOrganization"]:
            logger.info(_["url"])
            r = session.get(_["url"], headers=_headers)
            tree = html.fromstring(r.text)
            ll = "".join(tree.xpath("//div/@data-gmaps-static-url-mobile"))
            latitude = ll.split("center=")[1].split("%2C")[0].strip()
            longitude = ll.split("center=")[1].split("%2C")[1].split("&")[0].strip()
            hours_of_operation = (
                " ".join(
                    tree.xpath('//p[./strong[text()="Hours of Operation"]]//text()')
                )
                .replace("\n", "")
                .replace("Hours of Operation", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(tree.xpath('//p[contains(text(), "0pm")]//text()'))
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                location_type=_["@type"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                latitude=latitude,
                longitude=longitude,
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
