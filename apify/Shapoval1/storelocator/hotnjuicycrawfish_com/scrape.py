from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hotnjuicycrawfish.com"
    api_url = "https://www.hotnjuicycrawfish.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="link-block-3 w-inline-block"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.hotnjuicycrawfish.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@class="header pad-more"]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(tree.xpath('//a[contains(@href, "maps")]/text()')).replace(
            "#1114Phoenix", "#1114 Phoenix"
        )
        if location_name == "las vegas, NV - Planet Hollywood":
            ad = (
                " ".join(tree.xpath('//a[contains(@href, "maps")]/text()[2]'))
                .replace("\n", "")
                .strip()
            )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if "Ste C-D" in city:
            city = city.replace("Ste C-D", "").strip()
            street_address = street_address + " " + "Ste C-D"
        if "St" in city:
            city = city.replace("St", "").strip()
            street_address = street_address + " " + "St"
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "<MISSING>":
            map_link = "".join(tree.xpath("//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                tree.xpath('//div[@class="contact"]/following-sibling::div[1]//text()')
            )
            or "<MISSING>"
        )
        if location_name == "las vegas, NV - Planet Hollywood":
            phone = (
                " ".join(tree.xpath('//a[contains(@href, "maps")]/text()[1]'))
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="hours-div w-clearfix"]/p/text()'))
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
