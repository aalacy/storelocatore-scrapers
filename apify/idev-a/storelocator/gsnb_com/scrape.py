from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://gsnb.com"
base_url = "https://gsnb.com/about-us/locations/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.panel-grid-cell")
        for link in links:
            if not link.iframe or not link.p:
                continue
            block = []
            for bb in link.select("p")[::-1]:
                if not bb.text.strip():
                    continue
                block = list(bb.stripped_strings)
                break
            location_name = ""
            for aa in link.select("h3"):
                if not aa.text.strip():
                    continue
                location_name = aa.text.strip()
                break
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
                del block[-1]
            addr = parse_address_intl(" ".join(block))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            coord = link.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
