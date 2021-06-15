from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("tommyguns.com")

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://www.tommyguns.com"
    base_url = "https://ca.tommyguns.com/blogs/locations?view=json"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["locations"]
        logger.info(f"{len(locations)} found!")
        for _ in locations:
            if not _["check_in_url"] and not _["address"]:
                continue
            page_url = "https://ca.tommyguns.com" + _["url"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            logger.info(page_url)
            hours = []
            if soup1.select_one("div.store-details__content"):
                temp = list(
                    soup1.select_one("div.store-details__content").stripped_strings
                )[1:]
                for hh in temp:
                    if "re-open" in hh.lower():
                        continue
                    if (
                        hh != "TEMPORARILY CLOSED"
                        and hh.split("-")[0].strip() not in days
                    ):
                        break
                    hours.append(hh)
            addr = parse_address_intl(_["address"].strip())
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"].replace("–", "-"),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                country_code="CA",
                phone=_.get("phone_number"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
