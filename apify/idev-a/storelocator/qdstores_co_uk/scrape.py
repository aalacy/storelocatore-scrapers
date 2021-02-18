from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

locator_domain = "https://www.qdstores.co.uk/"
base_url = "https://www.qdstores.co.uk/static/store-finder.html"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Referer": "https://www.qdstores.co.uk/",
    }


def fetch_data():
    # with SgRequests() as session:
    # res = session.get(base_url, headers=_headers())
    # soup = (
    #     res.text.split("Stores =")[1]
    #     .strip()
    #     .split("// Initiates the class once the DOM is ready")[0]
    #     .strip()
    # )
    # json_data = (
    #     soup.replace("\t", "").replace("\n", "").replace("\r", "")[:-3] + "}"
    # )
    locations = json.loads()
    for _ in locations:
        hours = []
        for key, value in json.loads(_["open_hours"]).items():
            hours.append(f"{key}: {value[0]}")
        hours_of_operation = "; ".join(hours)
        record = SgRecord(
            page_url=_["website"],
            store_number=_["id"],
            location_name=_["title"],
            street_address=_["street"],
            city=_["city"],
            state=_["state"],
            zip_postal=_["postal_code"],
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
