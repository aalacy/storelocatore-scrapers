import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.sunflowerbank.com/locationapi/LocationData/GetSunflowerLocations/?latLong=&service=&radius=&state="
    r = session.get(api, headers=headers)
    text = r.json()["MapData"]
    js = json.loads(text)["Table"]

    for j in js:
        location_name = j.get("LocationName") or ""
        street_address = j.get("LocationAddress")
        city = j.get("LocationCity") or ""
        if city[0].isdigit():
            street_address = city
            city = location_name.split(",")[0].strip()
        state = j.get("LocationState")
        postal = j.get("LocationZip")
        country_code = "US"
        store_number = j.get("LocationID")
        slug = j.get("NodeAliasPath")
        page_url = f"https://www.sunflowerbank.com{slug}"
        phone = j.get("LocationPhone") or ""
        if "or" in phone:
            phone = phone.split("or")[0].strip()
        latitude = j.get("LocationLatitude")
        longitude = j.get("LocationLongitude")

        location_type = "Branch"
        if j.get("LocationIsATMOnly"):
            location_type = "ATM"

        _tmp = []
        source = j.get("LocationLobbyHours") or "<html>"
        tree = html.fromstring(source)
        hours = tree.xpath("//strong")
        for h in hours:
            day = "".join(h.xpath("./text()")).strip()
            inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
            _tmp.append(f"{day} {inter}")

        hours_of_operation = ";".join(_tmp)
        if "ment" in hours_of_operation:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.sunflowerbank.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
