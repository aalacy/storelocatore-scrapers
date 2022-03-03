from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="card border-primary p-2"]')
    for d in div:

        location_name = "".join(
            d.xpath('.//preceding::h3[@class="card-title"][1]//text()')
        ).strip()
        ad = (
            " ".join(d.xpath(".//div[./iframe]/preceding-sibling::p[1]//text()"))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split()).replace('"', "").strip()
        if ad.find("facebook") != -1:
            ad = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "TH"
        if ad != "<MISSING>":
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state
            postal = a.postcode
            country_code = "TH"
            city = a.city
        map_link = "".join(d.xpath(".//div/iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone_list = d.xpath('.//a[contains(@href, "tel")]//text()')
        phone_list = list(filter(None, [a.strip() for a in phone_list]))
        phone = "".join(phone_list[0]).replace("​ ", "").strip()
        if phone.find("(") != -1:
            phone = phone.split("(")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/picture[.//img[@alt="clock.png"]]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
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
    locator_domain = "https://www.decathlon.co.th/"
    page_url = "https://www.decathlon.co.th/page/stores-location.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
