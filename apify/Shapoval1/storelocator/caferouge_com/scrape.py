from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.caferouge.com/"
    api_url = "https://www.caferouge.com/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "/restaurants/")]')
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        if (
            page_url
            == "https://www.caferouge.com/restaurants/haywards-heath/the-broadway"
        ):
            r = session.get("https://www.rougebrasserie.com/find")
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h2[@class="restaurant-title"]//text()'))
            or "<MISSING>"
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="address"]//text() | //div[@id="find-hayward-heath_overlay"]/div[2]/p[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = location_name
        if location_name == "<MISSING>":
            location_name = city
        text = "".join(tree.xpath('//a[contains(text(), "Get directions")]/@href'))
        try:
            latitude = text.split(",")[-2].split("/")[-1].strip()
            longitude = text.split(",")[-1]
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//a[@id="phonenumber"]/text() | //div[@id="find-hayward-heath_overlay"]//a[contains(@href, "tel")]/text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Opening Hours"]/following-sibling::text() | //div[@id="find-hayward-heath_overlay"]//h5[./strong[text()="Facilities"]]/preceding-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.count("CLOSED") == 7:
            hours_of_operation = "CLOSED"
        try:
            store_number = (
                "".join(tree.xpath('//script[contains(text(), "storeId")]/text()'))
                .split("storeId:")[1]
                .split(",")[0]
                .strip()
            )
        except:
            store_number = "<MISSING>"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
