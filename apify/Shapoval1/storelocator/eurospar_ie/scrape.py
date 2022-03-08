from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.eurospar.ie/"
    api_url = "https://www.eurospar.ie/wp-sitemap-posts-store-1.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(
                tree.xpath(
                    '//div[@class="section-store-information"]//*[@class="title-store-section"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="section-store-information"]//div[@class="store-address"]/p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        ad_lst = ad.split(",")
        state = a.state or "<MISSING>"
        for s in ad_lst:
            if "Co." in s or "Dublin" in s or "Co " in s:
                state = s.strip()
        if state.find("Dublin") != -1 and state.find("Co") == -1:
            state = state.split()[0].strip()
        postal = a.postcode or "<MISSING>"
        if postal == "H2YK":
            postal = ad.split(",")[-1].strip()
        country_code = "IE"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = state
        map_link = (
            "".join(
                tree.xpath(
                    '//div[@class="section-store-information"]//a[@class="get-directions"]/@href'
                )
            )
            or "<MISSING>"
        )
        try:
            latitude = map_link.split("=")[-1].split(",")[0].strip()
            longitude = map_link.split("=")[-1].split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="section-store-information"]//a[@class="telephone number"]/p/text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//ul[@class="table-hours"]/li//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Order") != -1:
            hours_of_operation = hours_of_operation.split("Order")[0].strip()
        if hours_of_operation.find("Bank") != -1:
            hours_of_operation = hours_of_operation.split("Bank")[0].strip()

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
