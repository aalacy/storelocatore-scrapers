from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sglogging import sglog

locator_domain = "https://www.pitapit.com.au/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "https://www.pitapit.com.au/store-locator"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    try:
        result = SgRequests.raise_on_err(session.get(api_url, headers=headers))
        log.info(f"## Response: {result}")

        tree = html.fromstring(result.text)
        div = tree.xpath('//div[contains(@class, "location_l ")]')
        for d in div:

            page_url = "https://www.pitapit.com.au/store-locator"
            location_name = "".join(d.xpath('.//div[@class="loc_item"]/h6[1]/text()'))
            ad = "".join(d.xpath('.//div[@class="text_part"]/text()'))
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            if street_address.find("Pita Pit Is Not Available") != -1:
                continue
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "AU"
            city = a.city or "<MISSING>"
            if city == "<MISSING>":
                city = " ".join(ad.split(",")[-1].split()[:-1]).strip()
                city = " ".join(city.split()[:-1])
            data_search = "".join(d.xpath(".//@data-search"))
            if state == "<MISSING>":
                state = data_search.split()[0].strip()
            latitude = "".join(d.xpath(".//@data-lat"))
            longitude = "".join(d.xpath(".//@data-lng"))
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
                .replace("(PITA)", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    d.xpath('.//button[@class="read-more"]/preceding::p[1]/text()')
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if hours_of_operation.find("Holidays") != -1:
                hours_of_operation = hours_of_operation.split("Holidays")[0].strip()

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
    except Exception as e:
        log.info(f"Err at #L100: {e}")


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
