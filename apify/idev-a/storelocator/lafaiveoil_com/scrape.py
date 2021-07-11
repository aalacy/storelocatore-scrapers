from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("lafaiveoil")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://www.lafaiveoil.com/"
    base_url = "http://www.lafaiveoil.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#wrapper table td")
        logger.info(f"{len(locations)} found")
        temp = []
        hours = []
        _hr = list(soup.select_one("div#sidebar").stripped_strings)
        for x, hh in enumerate(_hr):
            if "Mon" in hh:
                temp += _hr[x:]
                break

        for x, hh in enumerate(temp):
            if "Address" in hh:
                hours = temp[:x]
                break

        for _ in locations:
            if not _.text.strip():
                continue
            addr = parse_address_intl(" ".join(_.select("p")[1].stripped_strings))
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            yield SgRecord(
                page_url=base_url,
                location_name=addr.street_address_1,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=coord[1],
                longitude=coord[0],
                phone=_.select("p")[-1].text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
