from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.quiznos.com"
base_url = "https://restaurants.quiznos.com/api/stores-by-bounds?bounds=%7B%22south%22:-88.38648689578771,%22west%22:-180,%22north%22:89.86009095487248,%22east%22:180%7D"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()

        for _ in locations:
            street_address = _["address_line_1"]
            if _["address_line_2"]:
                street_address += " " + _["address_line_2"]
            phone = _["phone_number"]
            if phone:
                phone = phone.split("Ext")[0].strip()
            hours = []
            for day in days:
                day = day.lower()
                open = _[f"hour_open_{day}"]
                close = _[f"hour_close_{day}"]
                if "Open 24 Hours" in open:
                    hours.append(f"{day}: {open}")
                else:
                    hours.append(f"{day}: {open} - {close}")

            country_code = "USA"
            if _["province"] in ca_provinces_codes:
                country_code = "CA"

            yield SgRecord(
                page_url=_["order_url"] or "https://restaurants.quiznos.com/",
                store_number=_["number"],
                location_name=_["name"],
                street_address=street_address.replace("Gaetz Avenue Crossing", "")
                .replace("HMS Host, Honolulu International Airport", "")
                .replace("T. Turck Plaza - Swifties Food Mart", ""),
                city=_["city"],
                state=_["province"],
                zip_postal=_["postal_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
