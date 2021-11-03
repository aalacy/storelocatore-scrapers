from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("vacheron-constantin")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetch_data():
    locator_domain = "https://www.vacheron-constantin.com/"
    base_url = "https://stores.vacheron-constantin.com/locations.json"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["locations"]:
            _ = _["loc"]
            street_address = _["address1"].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            hours = []
            if _["hours"]:
                for hh in _["hours"]["days"]:
                    times = "closed"
                    if hh["intervals"]:
                        ii = hh["intervals"][0]
                        times = f"{_time(ii['start'])}-{_time(ii['end'])}"
                    hours.append(f"{hh['day']}: {times}")

            logger.info(_["url"])
            sp1 = bs(session.get(_["url"], headers=_headers).text, "lxml").select_one(
                ".LocationName-name"
            )
            location_type = ""
            if sp1 and "authorized retailer" in sp1.text.lower():
                location_type = "authorized retailer"
            else:
                location_type = "boutique"
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
