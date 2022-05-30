from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.preem.se/api/Stations/AllStations?$select=Id,Name,Address,PostalCode,City,PhoneNumber,StationType,StationSort,StationCardImage,OpeningHourWeekdayTime,ClosingHourWeekdayTime,OpeningHourSaturdayTime,ClosingHourSaturdayTime,OpeningHourSundayTime,ClosingHourSundayTime,CoordinateLatitude,CoordinateLongitude,Services/Name,Services/LinkedPage,Services/IconCssClass,FuelTypes/Name,FuelTypes/LinkedPage,FuelTypes/IconCssClass,FuelTypes/TextColor,FuelTypes/BackgroundColor,FuelTypes/BorderColor,FuelTypes/Type,FriendlyUrl,CampaignImage,CampaignUrl,TrailerRentalUrl,IsTrb,IsSaifa,IsSaifaStation,TillhorInternationellaAllianser&$expand=FuelTypes,Services&currentLanguage=sv"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        street_address = j.get("Address")
        city = j.get("City")
        postal = j.get("PostalCode") or ""
        if postal:
            if postal[-1].isalpha():
                postal = postal.split()[0]
        store_number = j.get("Id")
        location_name = j.get("Name")
        location_type = j.get("StationSort")
        slug = j.get("FriendlyUrl") or ""
        if slug.startswith("http"):
            page_url = slug
        else:
            page_url = f"https://www.preem.se{slug}"

        country_code = "SE"
        if ".no" in page_url:
            country_code = "NO"
        phone = j.get("PhoneNumber") or ""
        phone = phone.replace("Felanmälan Caverion", "").strip()
        if "(" in phone:
            phone = phone.split("(")[0]

        latitude = j.get("CoordinateLatitude")
        longitude = j.get("CoordinateLongitude")

        _tmp = []
        days = ["Weekday", "Saturday", "Sunday"]
        for day in days:
            start = j.get(f"OpeningHour{day}Time")
            end = j.get(f"ClosingHour{day}Time")

            if day == "Weekday":
                _tmp.append(f"Mon-Fri: {start}-{end}")
            else:
                _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
        if hours_of_operation.count("00:00") == 6:
            hours_of_operation = "24/7"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.preem.se/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
