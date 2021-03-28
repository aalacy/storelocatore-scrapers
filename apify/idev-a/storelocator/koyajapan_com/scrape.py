from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from lxml import html
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.strip().replace("–", "-").replace("’", "'")


def fetch_data():
    locator_domain = "https://koyajapan.com/"
    base_url = "https://koyajapan.com/locations/"
    with SgRequests() as session:
        soup = html.fromstring(session.get(base_url, headers=_headers).text)
        locations = soup.xpath(
            "//div[contains(@class, 'elementor-column elementor-col-50')]"
        )
        for _ in locations:
            if not "".join(_.xpath(".//text()")).strip():
                continue
            if re.search(r"coming soon", "".join(_.xpath(".//text()")), re.IGNORECASE):
                continue
            addr = _.xpath(".//p/text()")
            location_type = ""
            if re.search(r"TEMPORARILY CLOSED", addr[0], re.IGNORECASE):
                location_type = "TEMPORARILY CLOSED"
                del addr[0]
            zip_postal = addr[2]
            if len(addr) > 3 and re.search(r"ORDER ONLINE", addr[3], re.IGNORECASE):
                del addr[3]
            if re.search(r"ORDER ONLINE", addr[-1], re.IGNORECASE):
                del addr[-1]
            if len(addr) > 3 and re.search(r"OPEN from", addr[3], re.IGNORECASE):
                del addr[3]
            hours_of_operation = ""
            if len(addr) > 3:
                hours_of_operation = "; ".join(addr[3:])
            try:
                coord = (
                    _.xpath(".//a/@href")[-1]
                    .split("/@")[1]
                    .split("z/data")[0]
                    .split(",")
                )
                yield SgRecord(
                    page_url=base_url,
                    location_name=_.xpath(".//h2/text()")[0],
                    street_address=_valid(addr[0]),
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip(),
                    latitude=coord[0],
                    longitude=coord[1],
                    zip_postal=zip_postal,
                    country_code="US",
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation=_valid(hours_of_operation),
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
