from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("baptistonline")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.baptistonline.org"
base_url = "https://www.baptistonline.org/locations"
data = []


def _detail(link, location_type):
    page_url = locator_domain + link.a["href"]
    addr = list(link.select_one("p.location-address").stripped_strings)
    phone = ""
    if link.select_one(".location-phone"):
        phone = link.select_one(".location-phone").text.strip()
    if phone and f"{phone}" in data:
        return None
    if phone:
        data.append(f"{phone}")
    return SgRecord(
        page_url=page_url,
        location_name=link.select_one(".location-name").text.strip(),
        street_address=" ".join(addr[:-1]),
        city=addr[-1].split(",")[0].strip(),
        state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
        zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
        country_code="US",
        phone=phone,
        location_type=location_type,
        locator_domain=locator_domain,
        latitude=link.select_one('input[name="location-lat"]').get("value"),
        longitude=link.select_one('input[name="location-lng"]').get("value"),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#hospitals ul li")
        logger.info(f"{len(links)} found")
        for link in links:
            yield _detail(link, "hospital")
        links = soup.select("div#minormedicalcenters ul li")
        logger.info(f"{len(links)} found")
        for link in links:
            yield _detail(link, "medical center")
        links = soup.select("div#clinics ul li")
        logger.info(f"{len(links)} found")
        for link in links:
            yield _detail(link, "clinic")
        links = soup.select("div#specialtyfacilities ul li")
        logger.info(f"{len(links)} found")
        for link in links:
            yield _detail(link, "specialty facility")


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
