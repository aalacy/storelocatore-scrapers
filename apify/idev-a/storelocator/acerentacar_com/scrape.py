from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from datetime import datetime

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.acerentacar.com"
base_url = "https://www.acerentacar.com/_next/data/7t-yefaZGWA-O4Far4a4N/Locations.json"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _t(hh):
    return datetime.strptime(hh, "%Y-%m-%dT%H:%M:%S").strftime("%I:%M%p")


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["pageProps"][
            "locations"
        ]
        for _ in locations:
            street_address = _["addressOne"]
            if _["addressTwo"]:
                street_address += " " + _["addressTwo"]
            if not street_address and not _["city"]:
                continue
            hours = []
            hr = _.get("locationHours", {})
            for day in days:
                day = day.lower()
                times = None
                if hr.get(f"{day}Closed"):
                    times = "closed"
                else:
                    start = hr.get(f"{day}Open")
                    end = hr.get(f"{day}Close")
                    if start:
                        times = f"{_t(start)} - {_t(end)}"
                if times:
                    hours.append(f"{day}: {times}")

            zip_postal = _["postalCode"]
            if zip_postal == "0000" or zip_postal == "000000" or zip_postal == "00000":
                zip_postal = ""
            yield SgRecord(
                page_url=base_url,
                store_number=_["locationCode"],
                location_name=_["locationName"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=zip_postal,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["countryISO"],
                phone=_.get("phoneNumber"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
