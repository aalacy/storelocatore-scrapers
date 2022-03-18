from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

locator_domain = "https://omnifamilyhealth.org"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    for i in range(1, 100):
        api_url = f"https://omnifamilyhealth.org/locations/page/{i}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        try:
            r = SgRequests.raise_on_err(session.get(api_url, headers=headers))
            tree = html.fromstring(r.text)
            div = tree.xpath('//a[text()="View Details"]')
            for d in div:

                page_url = "".join(d.xpath(".//@href"))
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                location_name = "".join(tree.xpath("//h1/text()"))
                location_type = (
                    "; ".join(
                        tree.xpath(
                            '//h2[text()="Services"]/following-sibling::ul/li/text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                street_address = (
                    "".join(
                        tree.xpath(
                            '//h3[text()="Address"]/following-sibling::p[1]/span[1]/text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                ad = (
                    "".join(
                        tree.xpath(
                            '//h3[text()="Address"]/following-sibling::p[1]/span[2]/text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                state = ad.split(",")[1].split()[0].strip()
                postal = ad.split(",")[1].split()[1].strip()
                country_code = "US"
                city = ad.split(",")[0].strip()
                latitude = "".join(tree.xpath("//div/@data-lat"))
                longitude = "".join(tree.xpath("//div/@data-lng"))
                phone = (
                    "".join(
                        tree.xpath(
                            '//h3[text()="Phone"]/following-sibling::p[1]/text()'
                        )
                    )
                    .replace("\n", "")
                    .replace("-OMNI ", "")
                    .strip()
                    or "<MISSING>"
                )
                hours_of_operation = (
                    " ".join(tree.xpath('//div[@class="hours"]/p[1]/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
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
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=f"{street_address} {ad}",
                )

                sgw.write_row(row)

        except Exception as e:
            log.info(f"Err at #L100: {e}")
            return


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
