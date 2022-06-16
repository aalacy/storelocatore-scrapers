import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.houseoffraser.co.uk/stores/search?countryName=United%20Kingdom&countryCode=GB&lat=0&long=0&sd=500"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var stores =')]/text()"))
    text = text.split("var stores =")[1].split("var searchLocationLat")[0].strip()[:-1]
    js = json.loads(text)

    for j in js:
        street_address = j.get("address")
        city = j.get("town")
        postal = j.get("postCode")
        country_code = j.get("countryCode")
        store_number = j.get("code")
        page_url = f'https://www.houseoffraser.co.uk/{j.get("storeUrl")}'
        location_name = j.get("formattedStoreNameLong")
        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("storeType")

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
        hours = j.get("openingTimes") or []

        for h in hours:
            day = days[h.get("dayOfWeek")]
            start = h.get("openingTime")
            close = h.get("closingTime")
            if not start:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start} - {close}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
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
    locator_domain = "https://www.houseoffraser.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
