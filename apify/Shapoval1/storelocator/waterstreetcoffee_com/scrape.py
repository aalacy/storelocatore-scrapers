from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://waterstreetcoffee.com/"
    api_url = "https://waterstreetcoffee.com/pages/cafes"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h2[@class="featured-content--overline"]]')
    for d in div:

        slug = "".join(d.xpath('.//a[contains(text(), "Learn")]/@href'))
        page_url = f"https://waterstreetcoffee.com{slug}"
        location_name = "".join(d.xpath(".//h3//text()")).replace("\n", "").strip()
        location_type = "".join(d.xpath(".//h2//text()")).replace("\n", "").strip()
        info = d.xpath("./div[1]/p[2]/text()")
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "".join(info[0]).strip()
        state = "".join(info[1]).split(",")[1].split()[0].strip()
        postal = "".join(info[1]).split(",")[1].split()[1].strip()
        country_code = "US"
        city = "".join(info[1]).split(",")[0].strip()
        phone = "<MISSING>"
        for i in info:
            if "p:" in i:
                phone = str(i).replace("p:", "").strip()

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="map--hours"]//text()'))
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
