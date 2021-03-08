from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://freshrestaurants.com/"
        base_url = "https://freshrestaurants.com/wp-admin/admin-ajax.php?action=store_search&lat=0&lng=0&max_results=25&radius=5000000&autoload=1"
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            if _["country"] not in ["United States", "Canada", "USA"]:
                continue
            hours = []
            if _["hours"]:
                for hour in bs(_["hours"], "lxml").select("tr"):
                    hours.append(f"{hour.td.text}: {hour.select('td')[1].text}")
            location_name = _["store"].split("&#8211;")[0].split("\u2013")[0]
            if _["store"].split("&#8211;")[-1].strip() == "Coming Soon":
                hours = ["Coming Soon"]
            yield SgRecord(
                page_url="https://freshrestaurants.com/locations",
                location_name=location_name,
                street_address=f"{_['address']} {_['address2']}".strip(),
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                latitude=_["lat"],
                longitude=_["lng"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
