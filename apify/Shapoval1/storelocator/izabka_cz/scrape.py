import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://izabka.cz"
    api_url = "https://izabka.cz/prodejny/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="shop-single"]')
    for d in div:

        page_url = "https://izabka.cz/prodejny/"
        location_name = "".join(d.xpath('.//span[@class="shop-title"]/text()'))
        js_block = "".join(d.xpath(".//script/text()")).split("(")[1].split(")")[0]
        js = json.loads(js_block)
        ad = "".join(js.get("address"))
        adr = ad.replace("<br/>", " ").strip()
        street_address = (
            "".join(d.xpath('.//span[@class="shop-address"]/text()'))
            .split(",")[0]
            .strip()
        )
        country_code = "CZ"
        postal = ad.split("<br/>")[-1].strip()
        city = ad.split("<br/>")[-2].strip()
        for c in city:
            if c.isdigit():
                city = city.split()[0]
        if city.isdigit():
            city = ad.split("<br/>")[-1].split()[0].strip()
            postal = ad.split("<br/>")[-2].strip()

        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-long"))
        days = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        tmp = []
        for m in days:
            day = m
            time = js.get("schedule").get(f"{m}")
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
