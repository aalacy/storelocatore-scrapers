import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from urllib.parse import unquote


def fetch_data(sgw: SgWriter):

    locator_domain = "https://sigels.com/"
    api_url = "https://sigels.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block_l = tree.xpath("//script[contains(text(), 'web_data/sigel.json')]//text()")
    js_block_l = list(filter(None, [a.strip() for a in js_block_l]))
    js_block = (
        "".join(js_block_l[1])
        .split('= JSON.parse(decodeURIComponent("')[1]
        .split('"));')[0]
        .strip()
    )
    a = unquote(js_block)
    js = json.loads(a)
    for j in js["merchant_configs"]:

        b = j.get("merchant")
        page_url = "<MISSING>"
        location_name = b.get("name") or "<MISSING>"
        ad = b.get("address").get("full_address")
        location_type = b.get("merchant_type")
        street_address = (
            b.get("address").get("address_properties").get("street_address")
        )
        state = b.get("address").get("address_properties").get("state")
        postal = b.get("address").get("address_properties").get("zip")
        country_code = "US"
        city = b.get("address").get("address_properties").get("city")
        latitude = b.get("address").get("address_properties").get("lat")
        longitude = b.get("address").get("address_properties").get("lng")
        phone = b.get("phone_number")
        hours_of_operation = "<MISSING>"
        hours = b.get("business_hours")
        days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
        tmp = []
        if hours:
            for d in days:
                day = str(d).capitalize()
                opens = hours.get(f"{d}").get("opening")
                closes = hours.get(f"{d}").get("closing")
                line = f"{day} {opens} - {closes}"
                if opens is None and closes is None:
                    line = f"{day} Closed"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
