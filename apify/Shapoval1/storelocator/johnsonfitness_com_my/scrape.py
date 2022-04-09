from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitness.com.my/"
    page_url = "https://johnsonfitness.com.my/store-location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./ul/li/a[contains(@href, "goo")]]')
    for d in div:

        location_name = "".join(d.xpath(".//preceding::h2[1]//text()"))
        ad = "".join(d.xpath(".//preceding::div[3]//text()"))
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        postal = a.postcode or "<MISSING>"
        country_code = "MY"
        if street_address.find("41200") != -1:
            street_address = " ".join(ad.split(",")[:6]).strip()
            postal = ad.split(",")[6].split()[0].strip()
        street_address = " ".join(street_address.split())
        city = a.city or "<MISSING>"
        text = "".join(d.xpath("./ul/li[1]//a/@href"))
        latitude = text.split("ll=")[1].split("%2C")[0].strip()
        longitude = text.split("ll=")[1].split("%2C")[1].split("&")[0].strip()
        phone = "".join(d.xpath(".//preceding::ul[1]/li[1]/a//text()"))
        if phone.find(":") != -1:
            phone = phone.split(":")[1].strip()
        state = (
            "".join(d.xpath(".//preceding::div[@data-settings][1]//text()"))
            or "<MISSING>"
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
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
