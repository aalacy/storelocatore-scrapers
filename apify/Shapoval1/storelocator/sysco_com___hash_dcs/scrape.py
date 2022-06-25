import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sysco.com/"
    api_url = "https://www.sysco.com/Contact/Contact/Our-Locations.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "const locations =")]/text()'))
        .split("const locations =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    js = tuple(js)

    for j in js:
        if j == {}:
            continue
        jso = json.loads(json.dumps(j))
        for i in jso.values():
            page_url = (
                i.get("websiteUrl")
                or "https://www.sysco.com/Contact/Contact/Our-Locations.html"
            )
            if "sysco.com" not in page_url:
                page_url = "https://www.sysco.com/Contact/Contact/Our-Locations.html"
            location_name = "".join(i.get("displayName")) or "<MISSING>"
            if location_name.find("-") != -1:
                location_name = location_name.split("-")[0].strip()
            slug = "".join(i.get("@link"))
            location_type = (
                slug.split("Sysco/")[1].split("/")[0].replace("-", " ").strip()
            )
            street_address = i.get("street") or "<MISSING>"
            state = i.get("state") or "<MISSING>"
            if state == "0":
                state = "<MISSING>"
            postal = i.get("zip") or "<MISSING>"
            country_code = i.get("country") or "<MISSING>"
            city = i.get("city") or "<MISSING>"
            latitude = i.get("lat") or "<MISSING>"
            longitude = i.get("lng") or "<MISSING>"
            phone = i.get("mainPhone") or "<MISSING>"
            if str(phone).find("or") != -1:
                phone = str(phone).split("or")[0].strip()

            hours_of_operation = i.get("customerServiceHours") or "<MISSING>"

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
