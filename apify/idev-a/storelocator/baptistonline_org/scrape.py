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


def _h(v):
    _v = v.split("(")[0].replace("–", "-").replace("Visitor Hours", "")
    if "24 hour" in _v:
        return "open 24 hour"
    else:
        return _v


def _detail(link, location_type, session):
    page_url = link.a["href"]
    if "google.com" in page_url or "tel:" in page_url:
        page_url = ""
    elif not page_url.startswith("http"):
        page_url = locator_domain + link.a["href"]
    hours = []
    if page_url:
        logger.info(page_url)
        sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
        if sp1.select_one("div.location-details-holiday-notes"):
            temp = list(
                sp1.select_one("div.location-details-holiday-notes").stripped_strings
            )
            for x in range(0, len(temp), 2):
                if x == len(temp) - 1:
                    break
                _tt = temp[x].lower()
                if (
                    "fax" in _tt
                    or "call" in _tt
                    or "phone" in _tt
                    or "tel" in _tt
                    or "baptist" in _tt
                ):
                    break
                hours.append(f"{_h(temp[x])} {_h(temp[x+1])}")
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
        hours_of_operation=_h("; ".join(hours)),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#hospitals ul li")
        logger.info(f"hospital {len(links)} found")
        for link in links:
            yield _detail(link, "hospital", session)
        links = soup.select("div#minormedicalcenters ul li")
        logger.info(f"medical center {len(links)} found")
        for link in links:
            yield _detail(link, "medical center", session)
        links = soup.select("div#clinics ul li")
        logger.info(f"clinic {len(links)} found")
        for link in links:
            yield _detail(link, "clinic", session)
        links = soup.select("div#specialtyfacilities ul li")
        logger.info(f"specialty facility {len(links)} found")
        for link in links:
            yield _detail(link, "specialty facility", session)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
