import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.blue-tomato.com/"
    api_url = "https://www.blue-tomato.com/en-US/shops/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    div = tree.xpath('//a[text()="All shops"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        s_page_url = f"https://www.blue-tomato.com{slug}"
        country_code = s_page_url.split("/shops/")[1].split("/")[0].capitalize()
        r = session.get(s_page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = (
            "".join(tree.xpath('//script[contains(text(), "var allPos =")]/text()'))
            .split("var allPos =")[1]
            .strip()
        )
        js = json.loads(div)

        for j in js:

            page_url = f"https://www.blue-tomato.com/en-US/shop/{j.get('nameForUrl')}"
            street_address = f"{j.get('line1')} {j.get('line2')}".strip()
            state = "<MISSING>"
            postal = "".join(j.get("postalCode"))
            city = j.get("town")
            if postal.find(" ") != -1:
                state = postal.split()[1].strip()
                postal = postal.split()[0].strip()
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            try:
                r = session.get(page_url)
                tree = html.fromstring(r.text)
                location_name = "".join(tree.xpath('//span[@class="storename"]/text()'))
                phone = (
                    "".join(
                        tree.xpath(
                            '//div[text()="Contact"]/following-sibling::div//a[contains(@href, "tel")]//text()'
                        )
                    )
                    or "<MISSING>"
                )
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[text()="Opening hours"]/following-sibling::div//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                hours_of_operation = " ".join(hours_of_operation.split())
                cls = "".join(tree.xpath('//span[contains(text(), "closed")]/text()'))
                if cls and hours_of_operation == "<MISSING>":
                    hours_of_operation = "Closed"
            except:

                location_name = j.get("shopname")
                phone = "<MISSING>"
                hours = j.get("openingDays")
                tmp = []
                for h in hours:
                    day = h.get("weekDay")
                    opens = h.get("openingTime")
                    closes = h.get("closingTime")
                    line = f"{day} {opens} - {closes}"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)

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
                raw_address=f"{street_address} {city},{state} {postal}".replace(
                    "<MISSING>", ""
                ).strip(),
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
