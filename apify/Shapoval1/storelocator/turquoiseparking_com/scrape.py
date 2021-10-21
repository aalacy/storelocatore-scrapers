from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://turquoiseparking.com"
    api_url = "http://turquoiseparking.com/parking-locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath("//div[@data-options]/@data-options")).split('{"title"')

    for d in div:
        if not d:
            continue
        page_url = "http://turquoiseparking.com/parking-locations"
        location_name = d.split(':"')[1].split('"')[0].strip()
        latitude = d.split('"lat":"')[1].split('"')[0].strip()
        longitude = d.split('"lng":"')[1].split('"')[0].strip()
        slug = " ".join(location_name.split(" ")[:2])
        ad = "".join(tree.xpath(f'//span[contains(text(), "{slug}")]/text()'))
        if ad.find(")") != -1:
            ad = ad.split(")")[1].strip()
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[1].strip()
        try:
            phone = (
                d.split('<div class=\\"phone\\"><span dir=\\"ltr\\">')[1]
                .split("<")[0]
                .strip()
            )
        except:
            phone = "<MISSING>"

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
