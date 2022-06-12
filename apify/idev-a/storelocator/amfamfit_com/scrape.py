from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("’", "'")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    locator_domain = "https://amfamfit.com/"
    base_url = "https://amfamfit.com/wp-admin/admin-ajax.php?action=store_search&lat=37.34958&lng=-77.48041&max_results=1000&search_radius=5000&autoload=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            hours = []
            for hh in bs(_["hours"], "lxml").select("tr"):
                hours.append(f"{hh.select('td')[0].text}: {hh.select('td')[1].text}")
            yield SgRecord(
                store_number=_["id"],
                page_url=_["url"],
                location_name=_["store"],
                street_address=f"{_['address']} {_['address2']}",
                city=_["city"].replace(",", ""),
                state=_["state"],
                zip_postal=_["zip"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
