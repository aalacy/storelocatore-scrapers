from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(1, 10000):
        api_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=UKSBDAZIVAISUXSR&pageSize=100&page={i}"
        r = session.get(api_url)
        js = r.json()

        for j in js:
            j = j["store_info"]
            street_address = (
                f"{j.get('address')} {j.get('address_extended') or ''}".strip()
            )
            city = j.get("locality")
            location_name = f"{j.get('name')} {city}"
            state = j.get("region")
            postal = j.get("postcode")
            country_code = j.get("country")
            adr = street_address.replace(" ", "-").replace(",", "*").lower()
            page_url = f"https://locations.orangeleafyogurt.com/ll/{country_code}/{state}/{city}/{adr}"
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            location_type = j.get("Type")
            hours = j.get("store_hours") or ""

            _tmp = []
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            hours = hours.split(";")[:-1]
            i = 0
            for d in days:
                try:
                    time = hours[i].split(",")
                except IndexError:
                    i += 1
                    _tmp.append(f"{d}: Closed")
                    continue
                start = f"{time[1][:2]}:{time[1][2:]}"
                close = f"{time[2][:2]}:{time[2][2:]}"
                _tmp.append(f"{d}: {start} - {close}")
                i += 1

            hours_of_operation = ";".join(_tmp)
            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 100:
            break


if __name__ == "__main__":
    locator_domain = "https://www.orangeleafyogurt.com"

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
