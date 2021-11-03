from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pella")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _d(val):
    _val = ""
    for v in val:
        if v.isdigit():
            _val += v

    return _val


def fetch_data():
    locator_domain = "https://www.pella.com"
    base_url = "https://www.pella.com/how-to-buy/showrooms/"
    streets = []
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.directory--showroomsDirectory_CityList  li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            json_url = link["href"]
            if link["href"].endswith("/"):
                json_url = link["href"][:-1]
            json_url = "https://api.pella.com/location/v2/info/showroom/" + _d(
                json_url.split("-")[-1]
            )
            logger.info(json_url)
            _ = session.get(json_url, headers=_headers).json()
            if "error" in _:
                continue
            street_address = _["line_1"]
            if _["line_2"]:
                street_address += " " + _["line_2"]
            if street_address in streets:
                continue
            streets.append(street_address)
            hours = []
            hours.append(f"Monday: {_['hour_mon']}")
            hours.append(f"Tuesday: {_['hour_tue']}")
            hours.append(f"Wednesday: {_['hour_wed']}")
            hours.append(f"Thursday: {_['hour_thu']}")
            hours.append(f"Friday: {_['hour_fri']}")
            hours.append(f"Saturday: {_['hour_sat']}")
            hours.append(f"Sunday: {_['hour_sun']}")

            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["store_number"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                latitude=_["location"]["coordinates"][1],
                longitude=_["location"]["coordinates"][0],
                location_type=_["branch_type"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
