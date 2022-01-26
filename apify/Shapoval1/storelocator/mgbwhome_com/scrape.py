from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_info(page_url):

    session = SgRequests()
    r = session.post(page_url)
    tree = html.fromstring(r.text)
    phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()
    text = "".join(tree.xpath("//a/@href"))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    hours_of_operations = tree.xpath(
        '//h3[contains(text(), "HOURS")]/following-sibling::p[1]/text()'
    )
    hours_of_operations = list(filter(None, [a.strip() for a in hours_of_operations]))
    hours_of_operations = (
        "".join(hours_of_operations).replace("pm", "pm;") or "<MISSING>"
    )
    if hours_of_operations == "<MISSING>":
        hours_of_operations = tree.xpath(
            '//h3[contains(text(), "HOURS")]/following-sibling::text()'
        )
        hours_of_operations = list(
            filter(None, [a.strip() for a in hours_of_operations])
        )
        hours_of_operations = (
            "".join(hours_of_operations).replace("pm", "pm;") or "<MISSING>"
        )

    if hours_of_operations.find("pickup") != -1:
        hours_of_operations = hours_of_operations.split("pickup.")[1]
    return phone, latitude, longitude, hours_of_operations


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mgbwhome.com"
    session = SgRequests()
    countries = ["CA", "US"]

    for country in countries:
        data = {
            "dwfrm_storelocator_country": country,
            "dwfrm_storelocator_findbycountry": "Search",
        }

        r = session.post(
            "https://www.mgbwhome.com/on/demandware.store/Sites-MGBW-Site/en_US/Stores-FindStores",
            data=data,
        )
        tree = html.fromstring(r.text)
        tr = tree.xpath("//table[@id='store-location-results'][1]//tr")
        for t in tr:
            location_name = "".join(t.xpath('.//span[@itemprop="name"]/text()'))
            if location_name == "":
                continue
            street_address = (
                "".join(t.xpath('.//span[@itemprop="streetAddress"]/text()')).strip()
                or "<MISSING>"
            )
            city = (
                "".join(t.xpath('.//span[@itemprop="addressLocality"]/text()'))
                .replace(",", "")
                .strip()
            )
            postal = (
                "".join(t.xpath('.//span[@itemprop="postalCode"]/text()')).strip()
                or "<MISSING>"
            )
            state = "".join(
                t.xpath('.//span[@itemprop="addressRegion"]/text()')
            ).strip()
            page_url = (
                "".join(t.xpath('.//a[@itemprop="url"]/@href')).strip() or "<MISSING>"
            )
            if page_url.find("virtual-store") != -1:
                continue
            if page_url != "<MISSING>":
                phone, latitude, longitude, hours_of_operation = get_info(page_url)

            else:
                phone, latitude, longitude, hours_of_operation = (
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                )
            if street_address.find("-") != -1 and street_address.find("(") == -1:
                phone = street_address
                street_address = "<MISSING>"
            if not street_address[0].isdigit():
                r = session.get(page_url)
                tree = html.fromstring(r.text)
                street_address = (
                    "".join(
                        tree.xpath(
                            '//h3[text()="LOCATION"]/following-sibling::p[1]/text()[1] | //h3[contains(text(), "LOCATION")]/following-sibling::text()[1]'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if page_url.find("Toronto-Signature") != -1:
                session = SgRequests()
                r = session.get(page_url)
                trees = html.fromstring(r.text)
                street_address = (
                    "".join(trees.xpath('//div[@class="grid-span-3"]/text()[2]'))
                    .replace("\n", "")
                    .strip()
                )
            street_address = street_address.replace(
                "Tanger Outlets San Marcos", ""
            ).strip()
            country_code = country

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
