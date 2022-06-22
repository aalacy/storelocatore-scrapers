import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://applebees.com/"
    api_url = "https://maps.restaurants.applebees.com/api/getAsyncLocations?template=domain&level=domain&lat=35.884558999999996&lng=-78.6117549&radius=10000&limit=10000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["markers"]
    for j in js:
        info = j.get("info")
        a = html.fromstring(info)
        js_block = "".join(a.xpath("//div//text()"))
        j = json.loads(js_block)
        location_name = j.get("location_name") or "<MISSING>"
        street_address = (
            f"{j.get('address_1')} {j.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = j.get("region") or "<MISSING>"
        postal = j.get("post_code") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("fid") or "<MISSING>"
        page_url = f"https://restaurants.applebees.com/data/{store_number}/"
        latitude = j.get("lat")
        longitude = j.get("lng")
        r = session.get(page_url, headers=headers)
        try:
            js = r.json()[0]
        except:
            continue

        phone = js.get("local_phone") or "<MISSING>"
        hours = []
        days = js["hours_sets"]["primary"].get("days")

        if days:
            for day in days:
                if isinstance(days[day], list):
                    opening = days[day][0]["open"]
                    close = days[day][0]["close"]
                    hours.append(f"{day}: {opening}-{close}")
                else:
                    hour = days[day]
                    hours.append(f"{day}: {hour}")

            hours_of_operation = ",".join(hours)
        else:
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
