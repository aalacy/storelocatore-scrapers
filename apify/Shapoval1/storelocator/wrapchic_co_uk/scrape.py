from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wrapchic.co.uk/"
    page_url = "https://wrapchic.co.uk/find-wrapchic/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h2[@class="locationtitle"]]')
    for d in div:

        location_name = "".join(d.xpath(".//h2//text()")).replace("\n", "").strip()
        ad = (
            " ".join(d.xpath(".//h2/following-sibling::p[text()][1]//text()"))
            .replace("\n", "")
            .strip()
        )
        if ad.find("Unit F1") != -1:
            ad = (
                ad
                + " "
                + "".join(d.xpath(".//h2/following-sibling::p[text()][2]//text()"))
                .replace("\n", "")
                .strip()
                + " "
                + "".join(d.xpath(".//h2/following-sibling::p[text()][3]//text()"))
                .replace("\n", "")
                .strip()
                + " "
                + "".join(d.xpath(".//h2/following-sibling::p[text()][4]//text()"))
                .replace("\n", "")
                .strip()
            )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        if ad.find("Dubai") != -1:
            country_code = "Dubai"
        city = a.city or "<MISSING>"
        text = "".join(d.xpath('.//a[text()="View Map"]/@href'))
        latitude = text.split("@")[1].split(",")[0].strip()
        longitude = text.split("@")[1].split(",")[1].strip()
        info = d.xpath(".//p//text()")
        info = list(filter(None, [s.strip() for s in info]))
        phone = "<MISSING>"
        for i in info:
            if "Tel" in i or "0189" in i or "04 " in i:
                phone = str(i).replace("Tel:", "").strip()
        hours_of_operation = "<MISSING>"
        tmp = []
        for i in info:
            if (
                "Monday" in i
                or "Tuesday" in i
                or "Wednesday" in i
                or "Thursday" in i
                or "Friday" in i
                or "Saturday" in i
                or "Sunday" in i
                or "Every day" in i
            ):
                tmp.append(i)
            hours_of_operation = "; ".join(tmp).strip() or "<MISSING>"

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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
