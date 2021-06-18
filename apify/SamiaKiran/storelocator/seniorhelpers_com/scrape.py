import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "https://www.seniorhelpers.com/"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.seniorhelpers.com/our-offices/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "section", {"class": "article container max-960-container sh-pt-1"}
        ).findAll("li")
        for loc in loclist:
            page_url = loc.find("a")["href"]
            location_name = loc.find("a").text.split("|")[0]
            page_url = "https://www.seniorhelpers.com" + page_url
            log.info(page_url)
            r = session.get(page_url, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            temp_list = soup.findAll("div", {"class", "content-holder"})
            phone = temp_list[0].find("a", {"class", "tel"}).text
            hours_of_operation = (
                temp_list[1].text.replace("Hours", "").replace("\n", "")
            )
            address = " ".join(x.text for x in temp_list[2].findAll("p")).strip()
            if "License" in address:
                address = address.split("License")[0]
            elif "Certificate#" in address:
                address = address.split("Certificate#")[0]
            address = address.strip()
            raw_address = address.replace(",", " ")
            address = usaddress.parse(raw_address)
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
                locator_domain="https://www.seniorhelpers.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
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
