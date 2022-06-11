from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("crashchampions")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://crashchampions.com/"
base_url = "https://crashchampions.com/locations"


def _d(_):
    hours = []
    for hh in bs(_["hours"], "lxml").stripped_strings:
        if "hour" in hh.lower():
            break
        hours.append(hh)
    street_address = _["address"]["address1"]
    if _["address"]["address1"]:
        street_address += _["address"]["address2"]

    return SgRecord(
        page_url=_["url"],
        store_number=_["id"],
        location_name=_["name"],
        street_address=street_address,
        city=_["address"]["city"],
        state=_["address"]["state"],
        zip_postal=_["address"]["zip"],
        country_code="us",
        phone=_["phone_number"],
        latitude=_["address"]["lat"],
        longitude=_["address"]["lng"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours).replace("–", "-"),
        raw_address=_["address"]["formatted_address"],
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#dropdown-menu-9 a")
        logger.info(f"{len(links)} found")
        for link in links:
            state = link["href"].split("=")[-1]
            url = f"https://crashchampions.com/api/locations?filter=true&per_page=25&state={state}"
            locations = session.get(url, headers=_headers).json()["data"]
            logger.info(f"[{state}] {len(locations)} found")
            if type(locations) == dict:
                for x, _ in locations.items():
                    yield _d(_)
            else:
                for _ in locations:
                    yield _d(_)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
