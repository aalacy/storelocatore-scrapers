import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://espressohouse.com/"
    page_url = "https://espressohouse.com/coffee-shops/"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "coffeeShopsData")]/text()'))
        .split("window.coffeeShopsData = ")[1]
        .strip()
    )
    js = json.loads(js_block)
    for j in js:

        store_number = j.get("ID") or "<MISSING>"
        latitude = j.get("position").get("lat") or "<MISSING>"
        longitude = j.get("position").get("lng") or "<MISSING>"
        location_name = j.get("title") or "<MISSING>"
        info = j.get("infowindow")
        a = html.fromstring(info)
        ad = a.xpath("//*//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        phone = "".join(ad[2]).strip()
        street_address = "".join(ad[0]).strip()
        if street_address.replace(" ", "").replace("-", "").strip().isdigit():
            street_address = "<MISSING>"
            phone = "".join(ad[0])
        if phone == "Öppettider:":
            phone = "<MISSING>"
        adr = "<MISSING>"
        if street_address != "<MISSING>":
            adr = "".join(ad[1]).strip()

        postal = "<MISSING>"
        city = "<MISSING>"
        if adr != "<MISSING>":
            try:
                city = adr.split(",")[1].strip()
                postal = adr.split(",")[0].strip()
            except:
                city = adr
        postal = (
            postal.replace("Bremen", "")
            .replace("Stockholm", "")
            .replace("Stängt", "")
            .strip()
            or "<MISSING>"
        )
        page_url = "<MISSING>"

        hours_of_operation = (
            " ".join(ad).split("Öppettider:")[1].replace("Läs mer", "").strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=SgRecord.MISSING,
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
