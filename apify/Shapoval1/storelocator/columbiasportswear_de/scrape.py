from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from tenacity import retry, stop_after_attempt
import tenacity
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("columbiasportswear_de")
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}


@retry(stop=stop_after_attempt(20), wait=tenacity.wait_fixed(120))
def get_response(url):
    with SgRequests(timeout_config=600, verify_ssl=False) as http:
        response = http.get(url, headers=headers)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP SUCCESS STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbiasportswear.de"
    api_url = "https://www.columbiasportswear.de/DE/l/stores"
    logger.info(f"Pulling from {api_url}")
    r = get_response(api_url)

    tree = html.fromstring(r.text)
    div = tree.xpath("//p[./strong]")
    for d in div:
        page_url = "https://www.columbiasportswear.de/DE/l/stores"
        location_name = "".join(d.xpath("./strong/text()"))
        ad = " ".join(d.xpath("./text()")).replace("\n", "").split("Telefon")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "DE"
        city = a.city or "<MISSING>"
        info = d.xpath("./text()")
        phone = "<MISSING>"
        for i in info:
            if "Telefon" in i:
                phone = str(i).strip()
                if phone.find(":") != -1:
                    phone = phone.split(":")[1].strip()
        logger.info(f"Phone: {phone}")

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    logger.info("Scrape Started")
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
        logger.info("Finished")
