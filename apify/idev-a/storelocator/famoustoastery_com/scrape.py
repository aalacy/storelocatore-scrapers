from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://famoustoastery.com/"
        base_url = "https://famoustoastery.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.71289&max_results=1000&search_radius=500&autoload=1"
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"] + " " + _["address2"]
            soup = bs(
                session.get(f"{_['permalink']}?fancybox=true", headers=_headers).text,
                "lxml",
            )
            hours_of_operation = soup.select("div.wpsl-contact-details")[
                -1
            ].text.replace(",", ";")
            if re.search(r"Temporarily Closed", _["store"], re.IGNORECASE):
                hours_of_operation = "Temporarily Closed"
            location_name = " ".join(_["store"].split("&#8211;")[0].split(" ")[:-1])
            yield SgRecord(
                page_url=_["permalink"],
                store_number=_["id"],
                location_name=location_name,
                street_address=street_address.strip(),
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
