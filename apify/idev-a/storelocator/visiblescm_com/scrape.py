from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("visiblescm")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.visiblescm.com"
base_url = "https://www.visiblescm.com/contact/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.col-md-6.offset-sm-1 p")
        logger.info(f"{len(links)} found")
        for link in links:
            if "Parcel" in link.text:
                continue
            phone = ""
            country_code = "US"
            location_type = ""
            if link.strong:
                location_name = link.strong.text.strip()
                addr = parse_address_intl(" ".join(list(link.stripped_strings)[1:]))
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2

                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
                if addr.country:
                    country_code = addr.country
                location_type = link.find_previous_sibling("h2").text.strip()
            else:
                addr = list(link.stripped_strings)
                location_name = ""
                street_address = addr[0]
                city = addr[1].split(",")[0].strip()
                state = addr[1].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = addr[1].split(",")[1].strip().split(" ")[-1].strip()
                phone = addr[2].split(":")[-1].strip()
                location_type = "headquarter"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                phone=phone,
                location_type=location_type,
                country_code=country_code,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
