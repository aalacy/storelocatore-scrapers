from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fsbwa")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.fsbwa.com"
    base_url = "https://www.fsbwa.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location-list div.location-item.match")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            addr = list(sp1.select_one("div.address").stripped_strings)[-2:]
            latitude = res.split("var lat = ")[1].split("var lng = ")[0].strip()[1:-2]
            longitude = res.split("var lng = ")[1].split("if (")[0].strip()[1:-2]
            yield SgRecord(
                page_url=page_url,
                store_number=link["id"].replace("location", ""),
                location_name=sp1.h1.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=sp1.select_one("div.phone p").text.strip(),
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(
                    [hh.text for hh in sp1.select("div.hours p") if hh.text.strip()]
                ).replace("Normal business hours are", ""),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
