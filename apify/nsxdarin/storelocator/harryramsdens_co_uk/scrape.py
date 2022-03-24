from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.harryramsdens.co.uk/"
    urls = [
        "Pitstop|https://www.harryramsdens.co.uk/locations?service=3",
        "Restaurant|https://www.harryramsdens.co.uk/locations?service=1",
        "Takeaway|https://www.harryramsdens.co.uk/locations?service=2",
    ]
    for u in urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        location_type = u.split("|")[0].strip()
        r = session.get(u.split("|")[1], headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//a[.//button[text()="Full info"]]')
        for d in div:

            page_url = "".join(d.xpath(".//@href"))
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = "".join(tree.xpath("//title/text()")) or "<MISSING>"
            street_address = (
                "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
                or "<MISSING>"
            )
            postal = (
                "".join(tree.xpath('//span[@class="postalCode"]/text()')) or "<MISSING>"
            )
            country_code = (
                "".join(tree.xpath('//span[@itemprop="addressCountry"]/text()'))
                or "<MISSING>"
            )
            city = (
                "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
                or "<MISSING>"
            )
            latitude = "".join(tree.xpath("//div/@data-lat")) or "<MISSING>"
            longitude = "".join(tree.xpath("//div/@data-lng")) or "<MISSING>"
            phone = (
                "".join(tree.xpath('//span[@itemprop="telephone"]/text()'))
                or "<MISSING>"
            )
            hours_of_operation = "<MISSING>"
            if location_type == "Restaurant":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[./h4[text()="RESTAURANT"]]/following-sibling::div[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if location_type == "Takeaway":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[./h4[text()="TAKEAWAY "]]/following-sibling::div[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if location_type == "Restaurant" and hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[./h4[text()="RESTAURANT & TAKEAWAY"]]/following-sibling::div[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if location_type == "Takeaway" and hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[./h4[text()="RESTAURANT & TAKEAWAY"]]/following-sibling::div[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[./h4[text()="OPENING HOURS"]]/following-sibling::div[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            per_cls = "".join(
                tree.xpath('//*[contains(text(), "PERMANENTLY CLOSED")]/text()')
            )
            if per_cls:
                continue

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
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
