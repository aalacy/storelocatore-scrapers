from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curves.com.my"
    api_url = "https://curves.com.my/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//article[contains(@class, "mix portfolio_")]')
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="portfolio_link_for_touch"]/@href'))
        location_name = (
            "".join(d.xpath('.//h5[@class="portfolio_title"]//text()'))
            .replace("\n", "")
            .strip()
        )
        country_code = "MY"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(tree.xpath('//*[text()="Address"]/following-sibling::p/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "<MISSING>":
            map_link = (
                "".join(tree.xpath('//a[contains(@href, "maps")]/@href')) or "<MISSING>"
            )
            try:
                if map_link.find("ll=") != -1:
                    latitude = map_link.split("ll=")[1].split(",")[0]
                    longitude = map_link.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = map_link.split("@")[1].split(",")[0]
                    longitude = map_link.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//*[text()="Tel"]/following-sibling::p/a[1]/text()'))
            .replace("\n", "")
            .replace("\r", "")
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
