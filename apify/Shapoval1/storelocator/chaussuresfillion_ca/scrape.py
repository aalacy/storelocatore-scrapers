from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chaussuresfillion.ca/"
    api_url = "https://chaussuresfillion.ca/pages/nos-boutiques"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="boutiques"]//a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("https") == -1:
            page_url = f"https://chaussuresfillion.ca{page_url}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@class="page-title"]/text()'))
        info = tree.xpath(
            '//*[text()="Adresse"]/following-sibling::*[1]//text() | //h3[text()="Heures d’ouverture"]/preceding-sibling::p[1]//text() | //h3[text()="HEURES D’OUVERTURE"]/preceding-sibling::p[1]//text()'
        )
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "".join(info[0]).replace(",", "").strip()

        ad = "".join(info[1])
        if len(info) == 6:
            ad = "".join(info[1]) + " " + "".join(info[2])
        state = "<MISSING>"
        if ad.find("QC") != -1:
            state = "QC"
        postal = " ".join(ad.split()[-2:])
        country_code = "CA"
        city = ad.split()[0].strip()
        if ad.find(",") != -1:
            city = ad.split(",")[0].strip()
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except IndexError:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        phone = "".join(info[3]).replace("Tel", "").replace(":", "").strip()
        if phone.find("Sans") != -1:
            phone = "".join(info[2]).replace("Tel", "").replace(":", "").strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//*[text()="Heures d’ouverture"]/following-sibling::p[contains(text(), ":")]//text() | //*[text()="HEURES D’OUVERTURE"]/following-sibling::p[1]//text() | //*[text()="Heures d’ouverture"]/following-sibling::p[contains(text(), "Jeudi")]//text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
