from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.eko.ca/"
    base_url = "https://www.eko.ca/nos-stations"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("window.stationData =")[2].split("</script>")[0].strip()[:-1]
        )
        for _ in locations:
            hours = []
            for day, hh in _["station_schedule_en"].items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=base_url,
                location_name=_["station_name"],
                street_address=_["station_street"],
                city=_["station_city"],
                state=_["station_state"],
                zip_postal=_["station_zip"],
                latitude=_["station_lat"],
                longitude=_["station_lng"],
                country_code="CA",
                phone=_["station_phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
