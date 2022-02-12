from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "http://gumbyspizza.com"
    api_url = "http://gumbyspizza.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="whitebox"]')
    for d in div:

        page_url = f"http://gumbyspizza.com{''.join(d.xpath('.//@href'))}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        if location_name == "Gumby's Pizza , ":
            location_name = location_name.replace(" ,", ",") + "".join(
                tree.xpath("//h6/text()")
            )
        location_type = "Gumby's Pizza"
        street_address = (
            "".join(tree.xpath("//address/text()[1]")).replace("\n", "").strip()
            or "<MISSING>"
        )
        ad = (
            "".join(tree.xpath("//address/text()[2]")).replace("\n", "").strip()
            or "<MISSING>"
        )
        adrInfo = (
            "".join(tree.xpath("//h6/text()")).replace("\n", "").strip() or "<MISSING>"
        )
        a = parse_address(USA_Best_Parser(), adrInfo)
        state = a.state or "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"

        if ad != ",":
            city = ad.split(",")[0].strip()
            postal = ad.split(",")[1].strip()
        if location_name == "Gumby's Pizza, University Of Wisconsin - Madison ":
            state = "Wisconsin"
            city = "Madison"
        if location_name.find("Gumby's Pizza,") == -1:
            state = location_name.split(",")[1].strip()
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        phone = (
            "".join(tree.xpath('//p[@id="locationHours"]/text()[1]'))
            .replace("\n", "")
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//p[@id="locationHours"]/text()[position()>1]'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
