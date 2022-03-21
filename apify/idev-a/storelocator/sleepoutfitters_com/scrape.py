from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.sleepoutfitters.com/"
    base_url = "https://www.sleepoutfitters.com/store-locator"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("jsonLocations:")[1]
            .split("imageLocations:")[0]
            .strip()[:-1]
        )
        for _ in locations["items"]:
            hours = []
            for day, hh in json.loads(_["schedule_string"]).items():
                times = "closed"
                if hh[f"{day}_status"]:
                    times = f"{hh['from']['hours']}:{hh['from']['minutes']}-{hh['to']['hours']}:{hh['to']['minutes']}"
                hours.append(f"{day}: {times}")
            yield SgRecord(
                page_url=_["seo_url"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["region_code"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
