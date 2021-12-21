from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.solidcore.co"
    api_url = "https://www.solidcore.co/studios/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = tree.xpath('//script[contains(text(), "var locations =")]/text()')
    jsblock = list(filter(None, [a.strip() for a in jsblock]))

    jsblock = (
        "".join(jsblock)
        .split("var locations =")[1]
        .split("];")[0]
        .replace("[", "")
        .replace("]", "")
        .strip()
    )

    jsblock = (
        jsblock.replace("lat", '"lat"')
        .replace("lng", '"lng"')
        .replace("icon", '"icon"')
        .replace("infoWindow", '"infoWindow"')
        .replace("content", '"content"')
    )
    jsblock = "[" + jsblock + "]"
    jsb = eval(jsblock)

    for i in jsb:

        latitude = i.get("lat")
        longitude = i.get("lng")
        info = i.get("infoWindow").get("content")
        info = html.fromstring(info)
        page_url = "".join(info.xpath("//p/strong/a/@href"))
        location_name = "".join(info.xpath("//p/strong/a/text()"))
        location_type = "gym"
        street_address = "".join(info.xpath("//p[./strong/a]/text()[1]"))
        ad = "".join(info.xpath("//p[./strong/a]/text()[2]")).replace("\n", "").strip()
        phone = (
            "".join(info.xpath("//p[./strong/a]/text()[3]")).replace("\n", "").strip()
        ) or "<MISSING>"
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
