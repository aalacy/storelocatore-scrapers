from sgselenium.sgselenium import SgFirefox
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.worldwidegolfshops.com"
    api_url = "https://www.worldwidegolfshops.com/sitemap/store-locator.xml"
    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.content)
    urls = tree.xpath("//url/loc")
    for u in urls:
        page_url = "".join(u.xpath(".//text()"))
        if page_url.find("store/uinta-golf") == -1:
            continue
        with SgFirefox() as fox:
            fox.get(page_url)
            a = fox.page_source
            tree = html.fromstring(a)

            location_name = "".join(tree.xpath("//h1//text()"))
            ad = (
                " ".join(
                    tree.xpath(
                        '//div[@class="vtex-yext-store-locator-0-x-addressBlock t-body"]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )

            street_address = ad.split("  ")[0].strip()
            city = ad.split("  ")[1].split(",")[0].strip()
            state = ad.split(",")[1].strip()
            postal = ad.split(",")[2].strip()
            country_code = "US"
            phone = "".join(
                tree.xpath(
                    '//div[@class="vtex-flex-layout-0-x-flexCol vtex-flex-layout-0-x-flexCol--store-contacts  ml0 mr0 pl0 pr0      flex flex-column h-100 w-100"]/div[1]/div/div[1]/text()'
                )
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@class="vtex-yext-store-locator-0-x-hoursRow mv2 flex justify-between"]/div/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            map_link = "".join(
                tree.xpath(
                    '//a[@class="vtex-yext-store-locator-0-x-addressDirectionsLink"]/@href'
                )
            )
            session = SgRequests()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
            }
            r = session.get(map_link, headers=headers)
            tree = html.fromstring(r.text)
            ll = "".join(tree.xpath('//meta[@itemprop="image"]/@content'))
            latitude = ll.split("markers=")[1].split("%2C")[0].strip()
            longitude = ll.split("markers=")[1].split("%2C")[1].split("&")[0].strip()

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
