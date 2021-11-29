from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    api_url = "https://www.steelcitypizza.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="SubMenu-1"]/ul/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.steelcitypizza.com{slug}"
        location_name = "".join(d.xpath(".//text()"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        country_code = "US"
        ad = (
            " ".join(tree.xpath('//a[contains(@href, "maps")]/text()'))
            .replace("\n", "")
            .strip()
        )
        if ad.find("Get Directions") != -1:
            ad = ad.split("Get Directions")[0].strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()

        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        ll = "".join(tree.xpath('//div[@class="gmaps"]/@data-gmaps-static-url-mobile'))
        latitude = ll.split("center=")[1].split("%2C")[0].strip()
        longitude = ll.split("center=")[1].split("%2C")[1].split("&")[0].strip()
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./a[contains(@href, "tel")]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath('//div[./p[contains(text(), "Sun-Thurs")]]/p/text()')
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("UPDATED HOURS: ", "")
            .replace("UPDATED HOURS", "")
            .replace("    ", " ")
            .replace(" -   ", " - ")
            .strip()
        )
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.steelcitypizza.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
