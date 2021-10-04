from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "ray-ban_com__usa"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.ray-ban.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://stores.ray-ban.com/united-states"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loc_block = soup.findAll("li", {"class": "Directory-listTeaser"})
        for loc in loc_block:
            title = loc.find("a", {"class": "Teaser-nameLink"})
            link = title["href"]
            link = "https://stores.ray-ban.com/" + link
            title = title.text
            p = session.get(link, headers=headers)
            soup = BeautifulSoup(p.text, "html.parser")
            street1 = soup.find("span", {"class": "c-address-street-1"}).text
            street2 = soup.find("span", {"class": "c-address-street-2"})
            if street2 is None:
                street = street1
            else:
                street = street1 + " " + street2.text
            city = soup.find("span", {"class": "c-address-city"}).text
            pcode = soup.find("span", {"class": "c-address-postal-code"}).text
            state = soup.find("span", {"class": "c-address-state"})
            if state is None:
                state = "<MISSING>"
            else:
                state = state.text
            phone = soup.find("a", {"class": "Phone-link"})
            if phone is None:
                phone = "<MISSING>"
            else:
                phone = phone.text

            hours = soup.find("table", {"class": "c-hours-details"})
            if hours is not None:
                hours = hours.find("tbody").findAll("tr")
                hoo = ""
                for hr in hours:
                    hour = hr.text
                    hour = hour.replace("Mon", "Mon ")
                    hour = hour.replace("Tue", "Tue ")
                    hour = hour.replace("Wed", "Wed ")
                    hour = hour.replace("Thu", "Thu ")
                    hour = hour.replace("Fri", "Fri ")
                    hour = hour.replace("Sat", "Sat ")
                    hour = hour.replace("Sun", "Sun ")
                    hoo = hoo + ", " + hour
                hoo = hoo.lstrip(", ").strip()
            else:
                hoo = "<MISSING>"

            lat = soup.find("meta", {"itemprop": "latitude"})["content"]
            lng = soup.find("meta", {"itemprop": "longitude"})["content"]

            if (
                hoo
                == "Mon Closed, Tue Closed, Wed Closed, Thu Closed, Fri Closed, Sat Closed, Sun Closed"
            ):
                hoo = "Closed"

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hoo.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
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
