import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "consumersbank_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.consumers.bank/About-Us/Contact/Locations-Hours"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "DottedBorder"}).findAll(
            "div", {"class": "locationDetails"}
        )
        for loc in loclist:
            page_url = loc.find("a")["href"]
            page_url = "https://www.consumers.bank/" + page_url
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text
            temp_list = soup.find("div", {"id": "dnn_NPLeft6"}).findAll("p")
            address = temp_list[0].text.replace("\n", " ")
            phone = temp_list[1].find("a").text
            hours_of_operation = (
                soup.find("div", {"id": "dnn_NPRight6"})
                .find("p")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            coords = r.text.split('"center":{')[1].split("}", 1)[0]
            latitude = coords.split('"latitude":')[1].split(",", 1)[0]
            longitude = coords.split('"longitude":')[1]

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
            yield SgRecord(
                locator_domain="https://www.consumers.bank/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address,
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal,
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
