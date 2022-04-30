from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    for i in range(1, 10000):
        api_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=URTGGJIFYMDMAMXQ&multi_account=true&page={i}&pageSize=100"
        r = session.get(api_url)
        js = r.json()

        for j in js:
            page_url = "https://locations.visionworks.com" + j.get("llp_url")
            j = j["store_info"]
            street_address = (
                f"{j.get('address')} {j.get('address_extended') or ''}".strip()
            )
            location_name = j.get("name")
            city = j.get("locality")
            state = j.get("region")
            postal = j.get("postcode")
            if len(postal) == 4:
                postal = f"0{postal}"
            country_code = j.get("country")
            store_number = j.get("corporate_id")
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            location_type = j.get("Type")
            hours = j.get("hours")

            if hours:
                _tmp = []
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                i = 0
                for d in days:
                    try:
                        line = hours.split(";")[i]
                    except IndexError:
                        line = ""
                    if line.find(",") != -1:
                        start_time = (
                            f'{line.split(",")[1][:2]}:{line.split(",")[1][2:]}'
                        )
                        end_time = f'{line.split(",")[2][:2]}:{line.split(",")[2][2:]}'
                        _tmp.append(f"{d}: {start_time} - {end_time}")
                    else:
                        _tmp.append(f"{d}: Closed")
                    i += 1

                hours_of_operation = ";".join(_tmp) or "<MISSING>"
            else:
                status = j.get("status") or ""
                if status == "coming soon":
                    hours_of_operation = "Coming Soon"
                else:
                    hours_of_operation = status

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 100:
            break


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://visionworks.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
