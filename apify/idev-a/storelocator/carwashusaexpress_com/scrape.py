from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import demjson

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://carwashusaexpress.com/"
    base_url = "https://carwashusaexpress.com/wp-admin/admin-ajax.php?action=store_search&lat=39.73924&lng=-104.99025&max_results=5000&search_radius=5000&autoload=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            hours = []
            for tr in bs(_["hours"], "lxml").select("tr"):
                hours.append(f"{tr.select('td')[0].text}: {tr.select('td')[1].text}")
            location_name = _["store"].split("&#8211;")[0]
            location_type = ""
            if "Temporarily Closed" in _["store"]:
                location_type = "Temporarily Closed"
            state = _["state"]
            if not state:
                soup = demjson.decode(
                    session.get(_["url"], headers=_headers)
                    .text.split(".fusion_maps(")[1]
                    .split(");")[0]
                    .strip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\\", "")
                )
                state = soup["addresses"][0]["address"].split(" ")[-2]
            yield SgRecord(
                store_number=_["id"],
                page_url=_["url"],
                location_name=location_name,
                location_type=location_type,
                street_address=f"{_['address']} {_['address2']}",
                city=_["city"],
                state=state,
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=_["zip"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
