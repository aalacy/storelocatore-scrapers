import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://gulfoil.co.uk"
    page_url = "https://gulfoil.co.uk/forecourts/find-your-nearest-gulf-station/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "["
        + "".join(tree.xpath('//script[contains(text(), "pins")]/text()'))
        .split("pins: [")[1]
        .split("hideInitially")[0]
        .strip()
    )
    js_block = js_block[:-1]
    js = json.loads(js_block)
    for j in js:
        info = j.get("tooltipContent")
        a = html.fromstring(info)
        ad = (
            "".join(a.xpath('//div[@class="mpfy-tooltip-content"]/p/text()'))
            .replace("\n", "")
            .strip()
        )
        info = "".join(a.xpath('//div[@class="mpfy-tooltip-content"]/p/text()')).split(
            ","
        )
        info = list(filter(None, [a.strip() for a in info]))
        location_name = j.get("title")
        a = parse_address(International_Parser(), ad)
        street_address = "<MISSING>"
        for i in info:
            if "Road" in i or "Street" in i:
                street_address = "".join(i)
        if street_address == "<MISSING>":
            street_address = "".join(info[1])
        if len(street_address) < 6:
            street_address = " ".join(info[:2])
        state = a.state or "<MISSING>"
        postal = ad.split(",")[-1].strip()
        if postal.find("Cheltenham") != -1:
            postal = postal.replace("Cheltenham", "").strip()
        country_code = "UK"
        city = a.city or "<MISSING>"
        latitude = j.get("latlng")[0]

        longitude = j.get("latlng")[1]
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
