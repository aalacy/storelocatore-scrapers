import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.ae/"
    api_url = "https://cars.honda.ae/en/our-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath('//script[contains(text(), "locationList")]/text()'))
    js = json.loads(div)
    for j in js["props"]["pageProps"]["locationLists"]["locationList"]:

        slug = j.get("name")
        page_url = f"https://cars.honda.ae/en/our-locations/{slug}/"
        location_name = j.get("Location_Name")
        location_type = j.get("LocationType")
        street_address = (
            "".join(j.get("Address")).replace("\n", "").replace("\r", "").strip()
        )
        country_code = "AE"
        city = j.get("emirates")
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        map_link = "".join(tree.xpath('//script[@type="application/json"]/text()'))
        s_js = json.loads(map_link)["props"]["pageProps"]["locationDetail"]
        map_link = s_js.get("Google_Map")
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        store_number = s_js.get("Location_Id")
        phone_list = tree.xpath('//a[contains(@href, "tel")]/@href')
        phone = "".join(phone_list[0]).replace("tel:", "").strip()
        hours_of_operation = f"{s_js.get('Opening_Time')} - {s_js.get('Closing_Time')}"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
