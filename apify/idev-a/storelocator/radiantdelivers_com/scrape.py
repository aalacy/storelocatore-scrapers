from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("radiantdelivers")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://rgl.radiantdelivers.com"
base_url = "https://rgl.radiantdelivers.com/contact-us"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.accordion div.collapse div.accordion__body")
        logger.info(f"{len(links)} found")
        for link in links:
            location_name = ""
            addr = None
            phone = ""
            street_address = ""
            zip_postal = ""
            blocks = link.findChildren(recursive=False)
            for x, bb in enumerate(blocks):
                if not bb.text.strip():
                    continue
                if (bb.name == "h3" and addr) or x == len(blocks) - 1:
                    yield SgRecord(
                        page_url=base_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=addr.city,
                        state=addr.state,
                        zip_postal=zip_postal,
                        country_code=addr.country,
                        phone=phone,
                        locator_domain=locator_domain,
                    )
                    location_name = phone = street_address = zip_postal = ""
                    addr = None
                if bb.name == "h3":
                    location_name = bb.text.strip()
                elif bb.name == "p" and "Visit Website" not in bb.text:
                    addr = parse_address_intl(" ".join(bb.stripped_strings))
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    zip_postal = addr.postcode
                    if zip_postal == "00000":
                        zip_postal = ""
                    if addr.country == "Japan":
                        street_address = (
                            " ".join(bb.stripped_strings).split(",")[0].strip()
                        )
                elif (
                    "Telephone" in bb.text or "Toll free" in bb.text
                ) and bb.name == "div":
                    phone = bb.a.text.strip()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
