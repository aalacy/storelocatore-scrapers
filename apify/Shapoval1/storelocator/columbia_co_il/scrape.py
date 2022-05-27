from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbia.co.il"
    api_url = "https://www.columbia.co.il/stores"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h2]")
    for d in div:

        page_url = "https://www.columbia.co.il/stores"
        location_name = "".join(d.xpath("./h2/text()")) or "<MISSING>"
        info = d.xpath(
            './div[@class="store-locator-content"]/ul/li/text() | ./div/p/text()'
        )
        ad = (
            " ".join(
                d.xpath(
                    './div[@class="store-locator-content"]/ul/li/text() | ./div/p/text()'
                )
            )
            .replace("\n", "")
            .split(":שעות פתיחה")[0]
            .strip()
        )
        ad = ad.split("שעות פתיחה:")[0].strip()
        if ad.find("טלפון:") != -1:
            ad = ad.split("טלפון:")[0].strip()
        ad = ad.replace("כתובת:", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "IL"
        city = a.city or "<MISSING>"
        text = "".join(d.xpath(".//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        for i in info:
            if "טלפון:" in i:
                phone = str(i).replace("טלפון:", "").strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/li[contains(text(), "שעות פתיחה")]/following-sibling::li//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("נגישות:") != -1:
            hours_of_operation = hours_of_operation.split("נגישות:")[0].strip()

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
