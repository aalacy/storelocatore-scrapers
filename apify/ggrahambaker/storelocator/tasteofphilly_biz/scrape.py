import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "tasteofphilly_biz"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.tasteofphilly.biz/locations/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.tasteofphilly.biz/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "et_pb_text_inner"})[:-2]
        for loc in loclist:
            page_url = "https://www.tasteofphilly.biz" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll("div", {"class": "et_pb_text_inner"})
            location_name = temp[0].text
            if "Having lunch or dinner at one of our restaurants" in temp[1].text:
                temp = soup.findAll("div", {"class": "et_pb_text_inner"})[6]
                hours_of_operation = (
                    r.text.split("Every Day")[1]
                    .split("</p>")[0]
                    .replace("</strong>", "")
                )
                hours_of_operation = "Every Day" + hours_of_operation
                if "</div>" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("</div>")[0]
                temp = temp.get_text(separator="|", strip=True).split("|")
                address = temp[0] + " " + temp[1]
                phone = temp[2]
            else:
                temp = temp[1].findAll("p")
                address = temp[0].get_text(separator="|", strip=True).replace("|", " ")
                phone = temp[1].find("a").text
                hours_of_operation = (
                    temp[2]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Hours", "")
                )
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
            country_code = "US"
            coords = soup.find("iframe")["src"]
            r = session.get(coords, headers=headers)
            coords = r.text.split("],0,1")[0].rsplit("[null,null,", 1)[1].split(",")
            latitude = coords[0]
            longitude = coords[1]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
