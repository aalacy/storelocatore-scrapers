from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json

locator_domain = "https://www.lassens.com/"
base_url = "https://www.lassens.com/wp-admin/admin-ajax.php?action=store_search&lat=34.0892&lng=-118.310875&max_results=15&search_radius=50&autoload=1"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        locations = json.loads(res.text)
        for _ in locations:
            hours = []
            for hour in bs(_["hours"], "lxml").select("tr"):
                hours.append(
                    f'{hour.select("td")[0].text}: {hour.select("td")[1].text.strip()}'
                )
            hours_of_operation = "; ".join(hours)
            record = SgRecord(
                page_url=urljoin("https://www.lassens.com", _["url"]),
                store_number=_["id"],
                location_name=_["store"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
