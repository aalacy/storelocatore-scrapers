from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("sasktel")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.sasktel.com/"
    base_url = "https://www.sasktel.com/dealers/"
    json_url = "https://www.sasktel.com/findadealer?lat=50.455&lng=-104.609&searchtype=locale&searchquery={}&sortby=dealername&limit=200&sortorder=asc&type=SKST"
    with SgRequests() as session:
        cities = [
            _.text.strip()
            for _ in bs(session.get(base_url, headers=_headers).text, "lxml").select(
                "section.locales-list ul li a"
            )
        ]
        logger.info(f"{len(cities)} cities found")
        for city in cities:
            locations = session.get(
                json_url.format(city.replace(" ", "%20")), headers=_headers
            ).json()["data"]
            for _ in locations:
                street_address = _["address"]["line1"]
                if _["address"]["line2"]:
                    street_address += " " + _["address"]["line2"]
                phone = ""
                if _["contacts"]["tel"]:
                    phone = _["contacts"]["tel"][0]
                hours = []
                for hh in bs(_["hours"], "lxml").stripped_strings:
                    if "Hours" in hh or "Book" in hh:
                        continue
                    hours.append(hh)
                yield SgRecord(
                    page_url=base_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["address"]["city"],
                    zip_postal=_["address"]["postalCode"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="CA",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
