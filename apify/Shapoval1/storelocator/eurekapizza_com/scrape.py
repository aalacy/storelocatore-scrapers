from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.eurekapizza.com"
    api_url = "https://www.eurekapizza.com/order-now"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//span[./h3[text()]]")
    for d in div:

        slug = "".join(
            d.xpath(
                './/a[./span[text()="Visit Us"]]/@href | .//a[./span[text()="Order Now"]]/@href'
            )
        )
        page_url = slug
        if page_url.find("http") == -1:
            page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath(".//h3//text()"))
        street_address = (
            "".join(d.xpath(".//h3/following-sibling::div[1]/p[1]//text()"))
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(d.xpath(".//h3/following-sibling::div[1]/p[2]//text()"))
            .replace(",", "")
            .strip()
        )
        if ad == "Rogers AR":
            ad = (
                ad
                + " "
                + "".join(d.xpath(".//h3/following-sibling::div[1]/p[3]//text()"))
                .replace(",", "")
                .strip()
            )

        state = ad.split()[-2].strip()
        postal = ad.split()[-1].strip()
        country_code = "US"
        city = " ".join(ad.split()[:-2]).strip()
        phone = "".join(d.xpath('.//p[contains(text(), "(")]//text()'))
        latitude, longitude = "<MISSING>", "<MISSING>"
        if page_url.find("id") == -1:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            latitude = "".join(tree.xpath("//div/@data-lat"))
            longitude = "".join(tree.xpath("//div/@data-lng"))
        if page_url.find("id") != -1:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "Latitude")]/text()'))
                .split('"Latitude":"')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "Latitude")]/text()'))
                .split('"Longitude":"')[1]
                .split('"')[0]
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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
