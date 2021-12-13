from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitness.com.my"
    api_url = "https://johnsonfitness.com.my/outlets/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div/ul/li/a[contains(@href, "maps")]]')
    for d in div:

        page_url = "https://johnsonfitness.com.my/outlets/"
        location_name = "".join(d.xpath(".//preceding::p[1]/strong/text()"))
        ad = (
            "".join(
                d.xpath('.//b[contains(text(), "Address:")]/following-sibling::text()')
            )
            .replace("\n", "")
            .strip()
        )
        slug = " ".join(ad.split()[:2])
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "MY"
        city = a.city or "<MISSING>"
        text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
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
            latitude = (
                "".join(
                    d.xpath(
                        f'.//following::p[contains(text(), "{slug}")]/following::div[@data-lng][1]/@data-lat'
                    )
                )
                or "<MISSING>"
            )
            longitude = (
                "".join(
                    d.xpath(
                        f'.//following::p[contains(text(), "{slug}")]/following::div[@data-lng][1]/@data-lng'
                    )
                )
                or "<MISSING>"
            )
        phone = (
            "".join(
                d.xpath('.//b[contains(text(), "Phone:")]/following-sibling::text()')
            )
            .replace("\n", "")
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
