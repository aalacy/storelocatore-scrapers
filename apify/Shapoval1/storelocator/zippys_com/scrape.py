import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.zippys.com"
    api_url = "https://www.zippys.com/wp-admin/admin-ajax.php?action=store_search&lat=21.30694&lng=-157.85833&max_results=10&search_radius=50&autoload=1"
    with SgFirefox() as driver:

        driver.get(api_url)
        a = driver.page_source
        tree = html.fromstring(a)
        js_block = "".join(tree.xpath("//*//text()"))
        js = json.loads(js_block)

        for j in js:

            page_url = j.get("permalink")
            location_name = "".join(j.get("store")).replace("&#8217;", "`").strip()
            location_type = "Restaurant"
            street_address = f"{j.get('address')} {j.get('address2')}".strip()
            state = j.get("state")
            postal = j.get("zip")
            country_code = j.get("country")
            city = j.get("city")
            latitude = j.get("lat")
            longitude = j.get("lng")
            phone = j.get("phone")
            _tmp = []
            hours_of_operation = j.get("hours") or "<MISSING>"
            if hours_of_operation != "<MISSING>":
                h = html.fromstring(hours_of_operation)
                days = h.xpath("//td/text()")
                times = h.xpath("//td/time[2]/text()")
                for d, t in zip(days, times):
                    _tmp.append(f"{d.strip()}: {t.strip()}")
                hours_of_operation = ";".join(_tmp)
            if (
                page_url == "https://www.zippys.com/locations/zippys-pearlridge/"
                and hours_of_operation == "<MISSING>"
            ):
                hours_of_operation = "Closed"
            if (
                page_url == "https://www.zippys.com/locations/zippys-kaimuki/"
                and hours_of_operation == "<MISSING>"
            ):
                hours_of_operation = "Closed"
            if (
                page_url == "https://www.zippys.com/locations/zippys-waimalu/"
                and hours_of_operation == "<MISSING>"
            ):
                hours_of_operation = "Temporarily closed"

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
