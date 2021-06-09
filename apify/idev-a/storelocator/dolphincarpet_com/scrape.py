from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("dolphincarpet")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.dolphincarpet.com/"
    base_url = "https://www.dolphincarpet.com/Locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.gradient li")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            hours = []
            for hh in _.select("p"):
                if "Hours" in hh.text:
                    hours = list(hh.stripped_strings)[1:]
                    break

            coord = (
                _.select_one("div.mapright")
                .iframe["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!3d")
            )
            phone = (
                list(_.select_one("div.tel").stripped_strings)[0]
                .replace("Phone", "")
                .strip()
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=_.select_one("div.adr .street-address")
                .text.split("-")[0]
                .strip(),
                city=_.select_one("div.adr .locality").text.strip(),
                state=_.select_one("div.adr .region").text.strip(),
                zip_postal=_.select_one("div.adr .postal-code").text.strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
