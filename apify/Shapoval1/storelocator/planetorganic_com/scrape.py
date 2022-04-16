from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.planetorganic.com/"
    api_url = "https://www.planetorganic.com/pages/our-stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="stores-section-item"]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()"))
        if location_name.find("permanently closed") != -1:
            continue
        page_url = "".join(d.xpath('.//a[text()="VIEW DETAILS"]/@href'))
        if page_url.find("http") == -1:
            page_url = f"https://www.planetorganic.com{page_url}"
        ad = (
            " ".join(d.xpath('.//div[@class="rte"]/p/text()')).replace("\n", "").strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if page_url == "https://www.planetorganic.com/pages/spitalfields":
            city = "London"
            street_address = (
                "".join(d.xpath('.//div[@class="rte"]/p/text()[2]'))
                .replace("\n", "")
                .strip()
            )
            postal = (
                "".join(d.xpath('.//div[@class="rte"]/p/text()[3]'))
                .replace("\n", "")
                .strip()
            )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        info = (
            " ".join(tree.xpath('//div[@class="store-details-address rte"]//text()'))
            .replace("\n", "")
            .strip()
        )
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        try:
            phone = info.split("Tel:")[1].strip()
        except:
            phone = "<MISSING>"
        if phone.find("Sign") != -1:
            phone = phone.split("Sign")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="store-details-opening rte"]//table//tr/td/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Coming Soon") != -1:
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
