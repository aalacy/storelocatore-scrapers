from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from datetime import datetime, timedelta

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.monsieurmuffler.com"
base_url = "https://www.monsieurmuffler.com/wp-json/wp/v2/lt_store_locator"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for loc in locations:
            _ = loc["postmetafields"]
            addr = _["address"]
            page_url = loc["link"]
            street_address = addr["address1"]["en"]
            if addr["address2"]["en"]:
                street_address += " " + addr["address2"]["en"]
            hours = []
            try:
                for day, hh in _.get("schedules", {}).items():
                    times = []
                    for hr in hh:
                        if hr["start"]:
                            if times:
                                if datetime.strptime(
                                    times[-1].split("-")[-1].strip(), "%H:%M"
                                ) + timedelta(hours=1) == datetime.strptime(
                                    hr["start"], "%H:%M"
                                ):
                                    _hh = f"{times[-1].split('-')[0]} - {hr['end']}"
                                    del times[-1]
                                    times.append(_hh)
                            else:
                                times.append(f"{hr['start']} - {hr['end']}")
                    if not times:
                        times = ["closed"]
                    hours.append(f"{day}: {','.join(times)}")
            except:
                pass
            yield SgRecord(
                page_url=page_url,
                store_number=loc["id"],
                location_name=_["name"]["en"],
                street_address=street_address,
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["zipcode"],
                latitude=addr["lat"],
                longitude=addr["long"],
                country_code=addr["country"],
                phone=_["communication"].get("primaryPhone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
