from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


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
        if page_url == "http://gumbyspizza.com/college-station":
            page_url = "https://www.gumbyspizzaaggieland.com/store-info/"
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
        if ad != "," and ad != "<MISSING>":
            city = ad.split(",")[0].strip()
            postal = ad.split(",")[1].strip()
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        if location_name.find(",") != -1 and street_address != "<MISSING>":
            state = location_name.split(",")[-1].strip()
        if location_name.find("Madison") != -1:
            city = "Madison"
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
        if page_url == "https://www.gumbyspizzaaggieland.com/store-info/":
            ad = (
                "".join(
                    tree.xpath('//div[./h1[text()="Info"]]/following-sibling::text()')
                )
                .replace("\n", "")
                .replace("\r", "")
                .split("Address:")[1]
                .strip()
            )
            street_address = " ".join(ad.split(",")[0].split()[:-2]).strip()
            city = " ".join(ad.split(",")[0].split()[-2:]).strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            phone = "".join(
                tree.xpath(
                    '//div[@class="fusion-title title"]/following-sibling::a[contains(@href, "tel")]/text()'
                )
            )
            location_name = f"Gumby's Pizza {city}, {state}"
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[./p[contains(text(), "am")]]/p[contains(text(), "am")]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            map_link = "".join(tree.xpath("//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
