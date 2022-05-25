from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(1, 100):
        api = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=AJXCZOENNNXKHAKZ&multi_account=false&page={i}&pageSize=100"
        r = session.get(api)
        js = r.json()

        for j in js:
            if isinstance(j, str):
                continue
            slug = j.get("llp_url")
            j = j["store_info"]
            page_url = f"https://locations.captainds.com{slug}"
            street_address = j.get("address")
            location_name = f"{j.get('name')} {street_address}".encode(
                "ascii", "ignore"
            ).decode()
            if (
                location_name.lower().find("closed") != -1
                or location_name.lower().find("coming") != -1
                or j.get("status") == "closed"
            ):
                continue
            city = j.get("locality")
            state = j.get("region")
            postal = j.get("postcode")
            country_code = j.get("country")
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            location_type = j.get("Type")
            hours = j.get("hours") or ""

            _tmp = []
            inters = {}
            days = {
                "1": "Mon",
                "2": "Tue",
                "3": "Wed",
                "4": "Thu",
                "5": "Fri",
                "6": "Sat",
                "7": "Sun",
            }

            for h in hours.split(";"):
                if not h:
                    continue

                line = h.split(",")
                start_time = f"{line[1][:2]}:{line[1][2:]}"
                end_time = f"{line[2][:2]}:{line[2][2:]}"
                inters[line[0]] = f"{start_time}-{end_time}"

            for index, day in days.items():
                inter = inters.get(index) or "Closed"
                _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                location_type=location_type,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 100:
            break


if __name__ == "__main__":
    locator_domain = "https://captainds.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
