from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("modernbeauty")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.modernbeauty.com"
    base_url = "https://www.modernbeauty.com/locations.html"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location_details")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["data-loc"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            try:
                state = (
                    bs(res, "lxml")
                    .select("div.font_size_8")[1]
                    .text.split(",")[1]
                    .strip()
                    .split(" ")[0]
                )
                _ = json.loads(
                    res.split("var locations =")[1]
                    .split("var ")[0]
                    .strip()[:-1]
                    .replace("\\n", "##")
                    .replace("\\r", "")
                    .replace("\\", "")
                )[0]
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["loc_value"].replace("NOW OPEN", ""),
                    street_address=_["address"].replace("##", ""),
                    city=_["city"],
                    state=state,
                    latitude=_["lat"],
                    longitude=_["long"],
                    zip_postal=_["postal_code"],
                    country_code="CA",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(_["store_hours"].split("##")),
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
