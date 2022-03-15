from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pizzatime.com/"
    api_url = "https://pizzatime.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "ORDER NOW")]')

    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        datas = (
            "".join(
                d.xpath(
                    './/preceding::a[contains(@href, "tel")][1]/preceding-sibling::text()'
                )
            )
            .split(",")[1]
            .replace("Seatac", "SeaTac")
            .strip()
        )
        latitude = "".join(
            d.xpath(f'.//following::div[@data-title="{datas}"]/@data-lat')
        )
        longitude = "".join(
            d.xpath(f'.//following::div[@data-title="{datas}"]/@data-lng')
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath(
                '//div[contains(@class, "et_pb_section et_pb_section_0")]//h2//text()'
            )
        )
        street_address = (
            "".join(tree.xpath('//div[./h4/span[text()="Address"]]/div/text()[1]'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//div[./h4/span[text()="Address"]]/div/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(
            tree.xpath(
                '//h4[./a[contains(@href, "tel")]]/following-sibling::div//text() | //h4[./span[contains(text(), "Phone")]]/following-sibling::div/text()'
            )
        )
        if phone.find("for") != -1:
            phone = phone.split("for")[0].strip()

        state = ad.split(",")[1].split()[0].strip()
        try:
            postal = ad.split(",")[1].split()[1].strip()
        except:
            postal = "<MISSING>"
        country_code = "US"
        city = ad.split(",")[0].strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[./h4/span[text()="Hours"]]/div//text()'))
            .replace("\n", "")
            .replace("|", "")
            .replace("&", "-")
            .strip()
        )
        if hours_of_operation.find("Last") != -1:
            hours_of_operation = hours_of_operation.split("Last")[0].strip()

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
