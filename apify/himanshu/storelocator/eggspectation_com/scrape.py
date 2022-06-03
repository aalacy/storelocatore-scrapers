from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.eggspectation.com/"
    api_url = "https://www.eggspectation.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[text()="USA - Locations"]/following-sibling::ul/li//a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.eggspectation.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
        ad = (
            "".join(tree.xpath('//div[@class="location-infod"]/p[1]/text()'))
            .replace("\n", " ")
            .strip()
        )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="location-infod"]/p/a[contains(@href, "tel")]//text()'
                )
            ).strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "Hours")]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("Opening Soon", "Coming Soon")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("Happy Hour: ") != -1:
            hours_of_operation = hours_of_operation.split("Happy Hour: ")[0].strip()
        ll = "".join(tree.xpath('//a[@class="directions"]/@href'))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll:
            latitude = ll.split("=")[-1].split(",")[0].strip()
            longitude = ll.split("=")[-1].split(",")[1].strip()

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
