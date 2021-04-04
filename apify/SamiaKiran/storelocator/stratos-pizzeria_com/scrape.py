from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "stratos-pizzeria_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        daylist = {
            "Dimanche": "Sunday",
            "Lundi": "Monday",
            "Mardi": "Tuesday",
            "Mercredi": "Wednesday",
            "Jeudi": "Thursday",
            "Vendredi": "Friday",
            "Samedi": "Saturday",
        }
        url = "https://stratos-pizzeria.com/wp-admin/admin-ajax.php?action=store_search&lat=46.81388&lng=-71.20798&max_results=100&search_radius=500&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            store_number = loc["id"]
            location_name = loc["store"]
            street_address = loc["address"]
            if not loc["address2"]:
                street_address = loc["address"] + " " + loc["address2"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            page_url = loc["url"]
            log.info(location_name)
            phone = loc["phone"]
            temp = BeautifulSoup(loc["description"], "html.parser")
            try:
                hour_list = temp.findAll("table")[1].findAll("tr")[1:]
            except:
                hour_list = temp.find("table").findAll("tr")[1:]
            hours_of_operation = ""
            for hour in hour_list:
                hour = hour.findAll("td")
                day = hour[0].text
                day = daylist[day]
                time = (
                    hour[1]
                    .text.replace("h", " ")
                    .replace("à", "-")
                    .replace("   ", " ")
                    .strip()
                )
                hours_of_operation = hours_of_operation + " " + day + " " + time
            yield SgRecord(
                locator_domain="https://stratos-pizzeria.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=location_name,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                store_number=store_number,
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
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
