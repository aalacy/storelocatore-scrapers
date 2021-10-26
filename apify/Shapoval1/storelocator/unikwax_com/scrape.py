from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://unikwax.com/"
    api_url = "https://unikwax.com/studio-locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[contains(@class, "location")]/a[1]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        cls = "".join(tree.xpath("//p/text()[2]")).replace("\n", "").strip()
        if "closed" in cls:
            continue
        ad = (
            "".join(tree.xpath('//a[@class="direction"]/@href'))
            .replace("<br> Opening Soon", "")
            .strip()
            or "<MISSING>"
        )
        if ad != "<MISSING>":
            ad = ad.split("=")[1].replace("Uni K Wax Studio", "").strip()
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//h5[contains(text(),"Moved To")]/following-sibling::p/text()[position()<3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )

        location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        if state == "City":
            state = "<MISSING>"
        if state == "New York New York":
            state = "New York"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if city == "Hoboken New":
            state = "New" + "" + state
            city = city.replace("New", "").strip()
        if city == "New":
            city, state = "New York", "New York"
        if location_name.find("Cutler Bay") != -1:
            city = "Cutler Bay"
            state = "FL"
        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "lat")]/text()'))
                .split('"lat":"')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "lat")]/text()'))
                .split('"lng":"')[1]
                .split('"')[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//a[@class="number"]//text() | //h5[contains(text(),"Moved To")]/following-sibling::p/text()[position()>2]'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h5[contains(text(), "Studio Hours")]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        cms = "".join(tree.xpath('//p[contains(text(),"soon")]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
