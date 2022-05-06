import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dollartree.com/"
    api_url = "https://www.dollartree.com/ccstoreui/v1/pages/layout/careers-logistics-map?ccvp=lg"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["regions"][3]["widgets"][2]["templateSrc"]
    js_block = (
        str(js)
        .split("setContextVariable:")[1]
        .split("<!")[0]
        .replace("}}} -->", "")
        .strip()
    )
    js_block = js_block.replace("\\", "").split('href="')[1:]
    for j in js_block:

        slug = str(j).split('"')[0].strip()
        page_url = f"https://www.dollartree.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        j_block = "".join(
            tree.xpath('//script[contains(text(), "streetAddress")]//text()')
        )
        js = json.loads(j_block)
        location_name = "".join(tree.xpath("//title//text()"))
        a = js.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        city = a.get("addressLocality") or "<MISSING>"
        store_number = js.get("@id")
        latitude = js.get("geo").get("latitude") or "<MISSING>"
        longitude = js.get("geo").get("longitude") or "<MISSING>"
        phone = js.get("telephone") or "<MISSING>"
        hours = js.get("openingHoursSpecification")
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")[0]
                opens = h.get("opens")
                closes = h.get("closes")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        if hours_of_operation.count("- ;") == 6:
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
