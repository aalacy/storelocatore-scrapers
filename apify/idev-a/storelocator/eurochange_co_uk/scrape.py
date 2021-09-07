from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.eurochange.co.uk"
base_url = "https://www.eurochange.co.uk/branches/GetBranches/51.5073509/-0.1277583?Latitude=51.5073509&longitude=-0.1277583"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _v(val):
    return val.replace("&#44;", ",").strip()


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            if _["ComingSoon"] != "N":
                continue
            page_url = f"https://www.eurochange.co.uk/branches/{_['SEOBranchNameLink']}"
            raw_address = _v(
                f"{_['AddressLine1']}, {_['AddressLine2']}, {_['AddressLine3']}, UK"
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            if _["Open24Hours"] == "N":
                for day in days:
                    _day = day.lower()
                    if _.get(f"{_day}Opening"):
                        start = _.get(f"{_day}Opening")
                        end = _.get(f"{_day}Closing")
                        if start == "Closed":
                            times = "Closed"
                        else:
                            times = f"{start} - {end}"
                        hours.append(f"{day}: {times}")
            else:
                hours = ["Open 24 hours"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["BranchId"],
                location_name=_["BranchName"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=_["Postcode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="UK",
                phone=_.get("TelephoneNo"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
