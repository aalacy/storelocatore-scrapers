import usaddress
from lxml import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mystricklands_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
locator_domain = "https://www.mystricklands.com/"
MISSING = SgRecord.MISSING


def fetch_data(sgw: SgWriter):

    api_url = "https://www.mystricklands.com/"
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[text()="LOCATIONS"]/following::ul[1]/li/a')
    for d in div:
        location_type = SgRecord.MISSING
        page_url = "".join(d.xpath(".//@href"))
        log.info(page_url)
        location_name = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        if 'alt="Closed -  relocating.png"' in r.text:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        if "CLOSED FOR THE" in r.text:
            address = (
                soup.findAll("div", {"data-testid": "richTextElement"})[2]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .split("CLOSED FOR THE ")[0]
            )
            location_type = "Temporarily Closed"
            phone = MISSING
            hours_of_operation = MISSING
        else:
            temp = (
                soup.findAll("div", {"data-testid": "richTextElement"})[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            try:
                address = temp.split("for employment.")[1].split("Phone")[0]
            except:
                address = temp.split("Liberty Court Plaza")[1].split("Phone")[0]
            try:
                phone = temp.split("Phone :")[1].split("Winter")[0]
            except:
                phone = temp.split("Phone :")[1]
            try:
                hours_of_operation = temp.split("Hours:")[1].split("OPEN 7 DAYS ")[0]
            except:
                hours_of_operation = temp.split("Hours")[1].split(
                    "Liberty Court Plaza"
                )[0]
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street_address = street_address + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                zip_postal = zip_postal + " " + temp[0]
            i += 1
        street_address = street_address.replace("(500 ft.", "")
        country_code = "US"
        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
