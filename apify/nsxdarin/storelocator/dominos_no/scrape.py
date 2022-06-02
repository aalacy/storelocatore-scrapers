import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dominos.no"
    api_url = "https://dominos.no/en/butikker"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath('//script[@type="application/json"]/text()'))
    js = json.loads(div)
    for j in js["props"]["pageProps"]["stores"]:

        slug = j.get("slug")
        page_url = f"https://dominos.no/en/butikker/{slug}"
        location_name = j.get("name") or "<MISSING>"
        a = j.get("address")
        street_address = a.get("street")
        postal = a.get("postalCode")
        country_code = a.get("country")
        city = a.get("city")
        store_number = j.get("externalId")
        latitude = a.get("location").get("latitude")
        longitude = a.get("location").get("longitude")
        hours = j.get("deliveryOptions").get("carryout").get("hoursOfOperation")
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            for h in hours:
                weekDay = h.get("weekDay")
                opens = h.get("openingHours")
                closes = h.get("closingHours")
                day = h.get("day")
                line = f"{weekDay} {day} {opens} - {closes}"
                if line.count("-") > 1:
                    continue
                tmp.append(line)
            hours_of_operation = "; ".join(tmp).replace("None", "").strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
