import json
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bikinivillage.com/en/"
    api_url = "https://www.bikinivillage.com/en/our-stores"

    with SgFirefox() as fox:
        fox.get(api_url)
        a = fox.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//a[./span[contains(text(), "Details")]]')
        for d in div:

            page_url = "".join(d.xpath(".//@href"))
            with SgFirefox() as fox:
                fox.get(page_url)
                a = fox.page_source
                tree = html.fromstring(a)

                location_name = "".join(
                    tree.xpath('//div[@class="store-title mb-1"]/text()')
                ).strip()
                ad = (
                    " ".join(
                        tree.xpath(
                            '//div[@class="tmx-store-info-container"]/div[contains(@class, "address")][1]//span//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                ad = " ".join(ad.split())
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                country_code = "CA"
                city = a.city or "<MISSING>"
                if (
                    page_url
                    == "https://www.bikinivillage.com/en/our-stores/0507-mississauga-square-one-centre"
                ):
                    state = "Ontario"
                    postal = "L5B2C9"
                if (
                    page_url
                    == "https://www.bikinivillage.com/en/our-stores/0566-victoria-mayfair-shopping-centre"
                ):
                    state = "British Columbia"
                    postal = "V8Z6E3"

                lljs = "".join(tree.xpath("//div/@data-stores-found"))
                js = json.loads(lljs)
                latitude = js.get("CenterLatitude")
                longitude = js.get("CenterLongitude")
                if (
                    page_url
                    == "https://www.bikinivillage.com/en/our-stores/0556-tsawwassen-first-nat-tsawwassen-mills"
                ):
                    latitude = js.get("CenterLongitude")
                    longitude = js.get("CenterLatitude")
                phone = (
                    "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()
                    or "<MISSING>"
                )
                if phone == "TBD":
                    phone = "<MISSING>"
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//i[@class="icon-icn-Clock-line-small pr-1"]/following::div[@class="js-container-details-0"][1]/div/div/text()'
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
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
