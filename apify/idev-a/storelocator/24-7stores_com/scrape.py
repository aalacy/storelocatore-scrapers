from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("24-7stores")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://24-7stores.com/"
    base_url = "https://24-7stores.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("table.locations-table tr.location")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.address.stripped_strings)
            script = json.loads(
                sp1.select_one("script#google-maps-builder-plugin-script-js-extra")
                .string.strip()
                .split("var gmb_data =")[1]
                .split("/* ]]> */")[0]
                .strip()[:-1]
            )
            location_name = list(sp1.select_one("div.address").stripped_strings)[0]
            coord = list(script.values())[0]["map_params"]
            yield SgRecord(
                page_url=page_url,
                store_number=link["data-location-id"],
                location_name=location_name,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                latitude=coord["latitude"],
                longitude=coord["longitude"],
                phone=sp1.select_one("a.phone-link").text.strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
