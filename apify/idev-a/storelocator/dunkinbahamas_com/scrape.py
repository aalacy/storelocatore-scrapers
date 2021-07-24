from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("dunkinbahamas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dunkinbahamas.com"
base_url = "https://www.dunkinbahamas.com/locations/"
json_url = "https://www.dunkinbahamas.com/?ajax=true&action=map_locations"


def coord(phone, location_name, locations):
    latitude = longitude = ""
    for _ in locations:
        if (
            _["phone"].strip() == phone.replace("\xa0", "")
            or location_name == _["title"].strip()
        ):
            latitude = _["latitude"]
            longitude = _["longitude"]
            break
    return latitude, longitude


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = session.get(json_url, headers=_headers).json()
        links = soup.select_one("div.main-content").findChildren(recursive=False)
        logger.info(f"{len(links)} found")
        for x, link in enumerate(links):
            if link.name == "h1":
                continue
            if link.name == "h3":
                location_name = link.text.replace("\xa0", " ").strip()
            if location_name == "Corporate Offices":
                break
            block = []
            if link.name == "p":
                block = list(link.stripped_strings)
            if location_name and block:
                latitude, longitude = coord(block[1], location_name, locations)
                hours_of_operation = block[-1].replace("–", "")
                if "Hours" in hours_of_operation:
                    hours_of_operation = ""
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    country_code="US",
                    phone=block[1].replace("\xa0", ""),
                    locator_domain=locator_domain,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=block[-1],
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
