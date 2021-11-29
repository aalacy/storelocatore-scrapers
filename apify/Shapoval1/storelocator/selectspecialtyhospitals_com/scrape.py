from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.selectspecialtyhospitals.com/"
    api_url = "https://www.selectspecialtyhospitals.com//sxa/search/results/?s={A9835FD2-AE76-4383-876E-44128806F6A6}|{A9835FD2-AE76-4383-876E-44128806F6A6}&itemid={9DE36713-213C-446D-A694-DEC9AC996203}&sig=&autoFireSearch=true&v=%7BE695F09C-8569-4B59-8EA8-F89CEF8FE995%7D&p=1000"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()["Results"]

    for j in js:
        cont = j.get("Html")
        a = html.fromstring(cont)
        page_url = "".join(a.xpath('//div[@class="loc-result-card-name"]/a/@href'))
        location_name = "".join(
            a.xpath('//div[@class="loc-result-card-name"]/a/text()')
        )
        location_type = "Regency Hospital"
        if page_url.find("regencyhospital") != -1:
            location_type = "Regency Hospital"
        if page_url.find("selectspecialtyhospitals") != -1:
            location_type = "Select Specialty Hospital"
        street_address = "".join(
            a.xpath('//a[contains(@href, "maps")]/text()[1]')
        ).strip()

        ad = (
            "".join(a.xpath('//a[contains(@href, "maps")]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(
            a.xpath(
                '//span[text()="PHONE"]/following-sibling::a[contains(@href, "tel")]/text()'
            )
        ).strip()
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        ll = "".join(a.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            latitude = ll.split("=")[2].split(",")[0].strip()
            longitude = ll.split(",")[-1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        try:
            tree = html.fromstring(r.text)
        except AttributeError:
            continue
        hooco = "".join(tree.xpath('//div[@class="field-businesshours"]/p/a/@href'))
        if hooco.find("http") == -1:
            hooco = f"https://www.selectspecialtyhospitals.com{hooco}"
        hours_of_operation = "<MISSING>"
        cls = "".join(tree.xpath('//div[contains(text(), "has Closed")]/text()'))
        if cls:
            hours_of_operation = "Closed"
        if hooco:
            r = session.get(hooco, headers=headers)
            try:
                tree = html.fromstring(r.text)
            except AttributeError:
                continue
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        '//p[contains(text(), "Hours:")]/text() | //strong[contains(text(), "hours")]/text() | //strong[contains(text(), "Hours:")]/text()'
                    )
                )
                .replace("Hours:", "")
                .replace("Visiting hours:", "")
                .strip()
                or "<MISSING>"
            )
            sub_info = (
                "".join(tree.xpath('//p[contains(text(), "Two visitors")]/text()'))
                .replace("\n", "")
                .strip()
            )
            if sub_info:
                hours_of_operation = sub_info.split("from")[1].split("The")[0].strip()

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
