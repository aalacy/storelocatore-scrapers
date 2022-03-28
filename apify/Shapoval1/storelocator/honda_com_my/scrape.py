from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.com.my"
    api_url = "https://www.honda.com.my/dealers"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "sc-showroom1")]')
    for d in div:

        page_url = "https://www.honda.com.my/dealers"
        location_name = "".join(d.xpath('.//div[@class="name"]/text()'))
        ad = (
            "".join(
                d.xpath(
                    './/div[@class="expand-content"]/div[@class="details"][1]/p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "MY"
        city = a.city or "<MISSING>"
        latitude = "".join(d.xpath(".//@data-gpslat"))
        longitude = "".join(d.xpath(".//@data-gpslong"))
        phone = "<MISSING>"
        info = d.xpath(
            './/div[@class="expand-content"]/div[@class="details"][2]/p/text()'
        )
        info = list(filter(None, [a.strip() for a in info]))
        for i in info:
            if "T:" in i or "Tel:" in i:
                phone = str(i).replace("T:", "").replace("Tel:", "").strip()
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()

        tmp = []
        for i in info:
            tmp.append(i)
            if "Service Centre" in i:
                break
        tmp_hours = []
        for i in tmp:
            if "0am" in i or "Closed" in i or " am" in i:
                tmp_hours.append(i)
        hours_of_operation = " ".join(tmp_hours) or "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
