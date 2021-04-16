from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("runnings")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.runnings.com/"
    base_url = "https://www.runnings.com/storelocator/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        options = soup.select("select#website-switcher option")
        logger.info(f"[total] {len(options)} found")
        for option in options:
            _ = session.get(
                f"https://www.runnings.com/storelocator/storedetails/post?id={option['value']}",
                headers=_headers,
            ).json()
            page_url = f"https://www.runnings.com/storelocator/storedetails?id={option['value']}"
            logger.info(page_url)
            hours = list(bs(_["operation_hours"], "lxml").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_number"],
                location_name=_["name"].strip(),
                street_address=", ".join(bs(_["street"], "lxml").stripped_strings),
                city=_["city"],
                state=_["region_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=_["postal_code"],
                country_code=_["country_id"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
