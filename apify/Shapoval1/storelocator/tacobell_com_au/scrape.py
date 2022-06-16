from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://tacobell.com.au/"
    api_url = "https://tacobell.com.au/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="theme_button mb_20"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@class="location-title"]/text()'))
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="address mb_20"]/*[contains(text(), "Address")]/text()'
                )
            )
            .replace("\n", "")
            .replace("Address:", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Australia"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = (
                location_name.replace("TACO BELL", "")
                .replace("Taco Bell", "")
                .strip()
                .capitalize()
            )
        try:
            latitude = (
                "".join(tree.xpath('//a[@class="get-direction-btn"]/@href'))
                .split("q=")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//a[@class="get-direction-btn"]/@href'))
                .split("q=")[1]
                .split(",")[1]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("Phone:", "")
            .strip()
        )
        hours_of_operation = (
            "".join(tree.xpath('//p[@class="opening_hours"]/text()'))
            .replace("Opening hours:", "")
            .replace("Regular", "")
            .replace("Address:", "")
            .strip()
        )
        if hours_of_operation.find("Hours:") != -1:
            hours_of_operation = hours_of_operation.split("Hours:")[1].strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
