from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://go-sport.com/"
    api_url = "http://stores.go-sport.com/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "magasin-sport")]')
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        except:
            continue
        location_name = "".join(tree.xpath('//h1[@class="nameShop"]/text()'))
        street_address = (
            "".join(tree.xpath('//span[@class="street1"]/text()')) or "<MISSING>"
        )
        postal = (
            "".join(tree.xpath('//span[@class="zipcode"]/text()'))
            .replace("P.O. Box", "")
            .replace("AZ", "")
            .replace("/", "")
            .replace("-", "")
            .strip()
            or "<MISSING>"
        )
        city = "".join(tree.xpath('//span[@class="city"]/text()')) or "<MISSING>"
        map_link = "".join(tree.xpath('//div[@class="backToList"]/a/@href'))
        try:
            latitude = map_link.split("/")[-2].split(",")[0].strip()
            longitude = map_link.split("/")[-2].split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="infosStore"]//span[@class="tel"]/following-sibling::text()[1]'
                )
            )
            .replace(":", "")
            .strip()
            or "<MISSING>"
        )
        mon = "".join(tree.xpath('//td[text()="Lundi"]/text()'))
        montime = (
            " ".join(tree.xpath('//table[@class="timeTable"]//tr[2]/td[1]//text()'))
            .replace("\n", " - ")
            .strip()
            + " - "
            + " ".join(tree.xpath('//table[@class="timeTable"]//tr[3]/td[1]//text()'))
            .replace("\n", " - ")
            .strip()
        )
        tue = "".join(tree.xpath('//td[text()="Mardi"]/text()'))
        tuetime = (
            " ".join(tree.xpath('//table[@class="timeTable"]//tr[2]/td[2]//text()'))
            .replace("\n", " - ")
            .strip()
            + " - "
            + " ".join(tree.xpath('//table[@class="timeTable"]//tr[3]/td[2]//text()'))
            .replace("\n", " - ")
            .strip()
        )
        wed = "".join(tree.xpath('//td[text()="Mercredi"]/text()'))
        wedtime = (
            " ".join(tree.xpath('//table[@class="timeTable"]//tr[2]/td[3]//text()'))
            .replace("\n", " - ")
            .strip()
            + " - "
            + " ".join(tree.xpath('//table[@class="timeTable"]//tr[3]/td[3]//text()'))
            .replace("\n", " - ")
            .strip()
        )
        thu = "".join(tree.xpath('//td[text()="Jeudi"]/text()'))
        thutime = (
            " ".join(tree.xpath('//table[@class="timeTable"]//tr[2]/td[4]//text()'))
            .replace("\n", " - ")
            .strip()
            + " - "
            + " ".join(tree.xpath('//table[@class="timeTable"]//tr[3]/td[4]//text()'))
            .replace("\n", " - ")
            .strip()
        )
        fri = "".join(tree.xpath('//td[text()="Vendredi"]/text()'))
        fritime = (
            " ".join(tree.xpath('//table[@class="timeTable"]//tr[2]/td[5]//text()'))
            .replace("\n", " - ")
            .strip()
            + " - "
            + " ".join(tree.xpath('//table[@class="timeTable"]//tr[3]/td[5]//text()'))
            .replace("\n", " - ")
            .strip()
        )
        sat = "".join(tree.xpath('//td[text()="Samedi"]/text()'))
        sattime = (
            " ".join(tree.xpath('//table[@class="timeTable"]//tr[2]/td[6]//text()'))
            .replace("\n", " - ")
            .strip()
            + " - "
            + " ".join(tree.xpath('//table[@class="timeTable"]//tr[3]/td[6]//text()'))
            .replace("\n", " - ")
            .strip()
        )
        san = "".join(tree.xpath('//td[text()="Dimanche"]/text()'))
        santime = (
            " ".join(tree.xpath('//table[@class="timeTable"]//tr[2]/td[7]//text()'))
            .replace("\n", " - ")
            .strip()
            + " - "
            + " ".join(tree.xpath('//table[@class="timeTable"]//tr[3]/td[7]//text()'))
            .replace("\n", " - ")
            .strip()
        )

        hours_of_operation = f"{mon}: {montime}; {tue}: {tuetime}; {wed}: {wedtime}; {thu}: {thutime}; {fri}: {fritime}; {sat}: {sattime}; {san}: {santime}"
        hours_of_operation = (
            hours_of_operation.replace("- - - - -", "Closed")
            .replace("- - -", "-")
            .replace("  - ", "")
            .strip()
        )
        if hours_of_operation.find(":;") != -1:
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=SgRecord.MISSING,
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
