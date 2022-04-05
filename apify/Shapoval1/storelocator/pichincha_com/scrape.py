import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pichincha.com/"
    api_url = "https://www.pichincha.com/portal/DesktopModules/PichinchaLocationsWeb/Search.ashx?method=province&_=1648913378683"

    with SgFirefox() as driver:
        driver.get(api_url)
        a = driver.page_source
        tree = html.fromstring(a)
        js_block = "".join(tree.xpath('//div[@id="json"]/text()'))
        js = json.loads(js_block)
        for j in js:

            state = j
            driver.get(
                f"https://www.pichincha.com/portal/DesktopModules/PichinchaLocationsWeb/Search.ashx?province={state}&method=city&_=1648913378685"
            )
            a = driver.page_source
            tree = html.fromstring(a)
            js_block = "".join(tree.xpath('//div[@id="json"]/text()'))
            js = json.loads(js_block)
            for j in js:
                city = j
                driver.get(
                    f"https://www.pichincha.com/portal/DesktopModules/PichinchaLocationsWeb/Search.ashx?province={state}&city={city}&types=1&method=search&_=1648913378686"
                )
                a = driver.page_source
                tree = html.fromstring(a)
                js_block = "".join(tree.xpath('//div[@id="json"]/text()'))
                js = json.loads(js_block)
                for j in js:

                    page_url = "https://www.pichincha.com/portal/geolocalizacion"
                    location_name = j.get("Name") or "<MISSING>"
                    street_address = j.get("Address") or "<MISSING>"
                    country_code = "Ecuador"
                    store_number = j.get("Id") or "<MISSING>"
                    latitude = j.get("Latitude") or "<MISSING>"
                    longitude = j.get("Longitude") or "<MISSING>"
                    phone = j.get("Phones") or "<MISSING>"
                    phone = str(phone).strip()
                    if str(phone).find("NE") != -1:
                        phone = "<MISSING>"
                    schedule_week = j.get("ScheduleWeek")
                    schedule_sat = j.get("ScheduleSat")
                    schedule_sun = j.get("ScheduleSun")
                    hours_of_operation = "<MISSING>"
                    if schedule_week:
                        hours_of_operation = str(schedule_week)
                    if schedule_sat:
                        hours_of_operation = hours_of_operation + " Sat " + schedule_sat
                    if schedule_sun:
                        hours_of_operation = hours_of_operation + " Sun " + schedule_sun
                    hours_of_operation = (
                        hours_of_operation.replace("Sat -Sun -", "")
                        .replace("Sun -", "")
                        .strip()
                    )

                    row = SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=SgRecord.MISSING,
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
