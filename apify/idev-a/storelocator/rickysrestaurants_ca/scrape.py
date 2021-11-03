from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://rickysrestaurants.ca/"
        base_url = "https://rickysrestaurants.ca/wp-admin/admin-ajax.php?action=location_search&lat=0&lng=0&max_results=1500&search_radius=500&autoload=1"
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = f"{_['address']} {_['address2']}"
            hours = []
            if _["hours"]:
                soup = bs(_["hours"], "lxml")
                for hour in soup.select("table.gssi-opening-hours tr"):
                    if len(hour.select("td")) < 2:
                        break
                    hours.append(
                        f"{hour.select_one('td').text}: {hour.select('td')[1].text}"
                    )
            yield SgRecord(
                store_number=_["id"],
                page_url=_["detail_url"],
                location_name=_["location"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
