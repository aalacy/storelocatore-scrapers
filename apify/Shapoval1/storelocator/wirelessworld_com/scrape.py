from datetime import datetime
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.wirelessworld.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "page.locations")]/text()'))
        .split("page.locations = ")[1]
        .split(";")[0]
        .strip()
    )

    js = json.loads(jsblock)
    for j in js:

        location_name = j.get("Name")
        street_address = f"{j.get('Address')} {j.get('Address2') or ''}".replace(
            "None", ""
        ).strip()
        phone = j.get("Phone")
        state = j.get("ProvinceAbbrev")
        postal = j.get("PostalCode")
        country_code = j.get("CountryCode")
        city = j.get("City")
        slug = "".join(city).lower().replace(" ", "-")
        store_number = j.get("LocationId")
        page_url = f"https://www.wirelessworld.com/locations/{store_number}/{slug}/"
        latitude = j.get("Google_Latitude")
        longitude = j.get("Google_Longitude")
        hours = j.get("HoursOfOperation")
        tmp = []
        for h in hours:
            day = h.get("DayOfWeek")
            try:
                opens = datetime.strptime(str(h.get("Open")), "%H%M").strftime(
                    "%I:%M %p"
                )
                close = datetime.strptime(str(h.get("Close")), "%H%M").strftime(
                    "%I:%M %p"
                )
            except:
                opens = "Closed"
                close = "Closed"
            line = f"{day} {opens} - {close}"
            if opens == "Closed" and close == "Closed":
                line = f"{day} - Closed"
            tmp.append(line)

        hours_of_operation = ";".join(tmp) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.wirelessworld.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
