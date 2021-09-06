from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgpostal.sgpostal import parse_address_intl
from ez_address_parser import AddressParser

ap = AddressParser()
session = SgRequests()
website = "thebrick_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    if True:
        url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=the-brick-furniture.myshopify.com&latitude=53.54178529302632&longitude=-93.91619999999999&max_distance=0&limit=300&calc_distance=0"
        loclist = session.get(url, headers=headers).json()["stores"]
        for loc in loclist:
            store_number = loc["store_id"]
            temp = loc["summary"]
            soup = BeautifulSoup(temp, "html.parser")
            location_name = soup.find("span", {"class": "name"}).text.strip()
            if "Distribution Centre" in location_name:
                continue
            if "Mattress Store" in location_name:
                location_name = "Brick Mattress Store"
            elif "Outlet" in location_name:
                location_name = "Brick Outlet"
            else:
                location_name = "Brick Store"
            try:
                page_url = soup.find("div", {"class": "store-page"}).find("a")["href"]
                page_url = "https://thebrick.com" + page_url
                temp_address = session.get(page_url, headers=headers)
                temp_address = BeautifulSoup(temp_address.text, "html.parser")
                raw_address = temp_address.find("div", {"id": "content"})[
                    "data-storecode"
                ]
                raw_address = (
                    "https://ecom.api.lflgroup.ca/ecom/stores/brick/" + raw_address
                )
                temp_list = session.get(raw_address, headers=headers).json()
                raw_address = temp_list["address"]["full"]
            except:
                page_url = "https://thebrick.com/apps/store-locator"
                raw_address = soup.find("span", {"class": "address"}).get_text(
                    separator=",", strip=True
                )
            log.info(page_url)

            formatted_addr = parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address is None:
                street_address = formatted_addr.street_address_2
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = formatted_addr.city
            state = formatted_addr.state if formatted_addr.state else "<MISSING>"
            zip_postal = formatted_addr.postcode
            if zip_postal is None:
                resultAddr = ap.parse(raw_address)
                for t, l in resultAddr:
                    if l == "PostalCode":
                        zip_postal = t
                    if l == "Province":
                        state = t
                    if l == "Municipality":
                        city = t

            hours = soup.find("span", {"class": "hours"})
            mo = hours.find("i", {"data-d": "M"}).find("i", {"data-l": "E"}).text
            tu = hours.find("i", {"data-d": "T"}).find("i", {"data-l": "E"}).text
            we = hours.find("i", {"data-d": "W"}).find("i", {"data-l": "E"}).text
            th = hours.find("i", {"data-d": "T"}).find("i", {"data-l": "E"}).text
            fr = hours.find("i", {"data-d": "F"}).find("i", {"data-l": "E"}).text
            sa = hours.find("i", {"data-d": "Sa"}).find("i", {"data-l": "E"}).text
            su = hours.find("i", {"data-d": "Su"}).find("i", {"data-l": "E"}).text
            hours_of_operation = (
                "Monday: "
                + mo
                + " Tuesday: "
                + tu
                + " Wednesday: "
                + we
                + " Thursday: "
                + th
                + " Friday: "
                + fr
                + " Saturday: "
                + sa
                + " Sunday: "
                + su
            )
            try:
                phone = soup.find("span", {"class": "phone"}).text.strip()
            except:
                phone = "<MISSING>"
            latitude = loc["lat"]
            longitude = loc["lng"]
            yield SgRecord(
                locator_domain="https://thebrick.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                store_number=store_number,
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
