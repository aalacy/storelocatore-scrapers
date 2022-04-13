from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "cafebrazil.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://cafebrazil.com"
    with SgRequests() as session:
        r = session.get(base_url + "/locations", headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        for i in soup.find_all("div", {"class": "col-sm-6 bb"}):
            dl = list(i.stripped_strings)
            location_name = dl[0]
            street_address = dl[1]
            city = dl[2].split(",")[0]
            state = dl[2].split(",")[1].strip().split(" ")[0]
            zipp = dl[2].split(",")[1].strip().split(" ")[1]
            phone = dl[3].replace("PH:", "").strip()
            hours_list = []
            for index in range(0, len(dl)):
                if "Hours" in dl[index] or "HOURS" in dl[index]:
                    hours_list = dl[index:]
                    break

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace("Hours:", "")
                .replace("HOURS:", "")
                .strip()
                .split("For Directions")[0]
                .strip()
                .split("Alcohol Served At This Location;")[0]
                .strip()
            )
            if len(hours_of_operation) > 0 and hours_of_operation[0] == ";":
                hours_of_operation = "".join(hours_of_operation)[1:].strip()

            if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
                hours_of_operation = "".join(hours_of_operation)[:-1].strip()

            map_url = i.find("a")["href"]
            lat, lng = get_latlng(map_url)

            yield SgRecord(
                locator_domain=website,
                page_url="https://www.cafebrazil.com/locations/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
