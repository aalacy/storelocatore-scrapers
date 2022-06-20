from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.replace(")", "")
        .replace("(", "")
        .replace("-", "")
        .replace(" ", "")
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://diyhomecenter.net/"
    base_url = "https://diyhomecenter.net/"
    with SgRequests() as session:
        hours_page = bs(
            session.get("https://diyhomecenter.net/contact-us/", headers=_headers).text,
            "lxml",
        )
        items = hours_page.find_all(class_="g-block size-25")
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.find(class_="g-dropdown-column").find_all("li")[1:]
        for link in links:
            soup1 = bs(session.get(link.a["href"], headers=_headers).text, "lxml")
            addr = list(soup1.select_one("div#custom-5926-particle").stripped_strings)
            block = list(soup1.select_one("div#custom-9810-particle").stripped_strings)
            try:
                map_link = soup1.find(id="custom-5926-particle").a["href"]
                lat_pos = map_link.rfind("!3d")
                latitude = map_link[
                    lat_pos + 3 : map_link.find("!", lat_pos + 5)
                ].strip()
                lng_pos = map_link.find("!2d")
                longitude = map_link[
                    lng_pos + 3 : map_link.find("!", lng_pos + 5)
                ].strip()
            except:
                latitude = ""
                longitude = ""
            phone = ""
            if _phone(addr[-1]):
                phone = addr[-1]
            if _phone(block[0]):
                phone = block[0]
            location_name = addr[0]
            for item in items:
                if item.p.text.upper() in location_name.upper():
                    hours_of_operation = " ".join(list(item.stripped_strings)[3:-1])
                    break
            yield SgRecord(
                page_url=link.a["href"],
                location_name=location_name,
                street_address=addr[1],
                city=addr[2].split(",")[0].strip(),
                state=addr[2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[2].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
