import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "dtsb_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://dtsb.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.dtsb.com/warehousing/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "et_pb_button et_pb_promo_button"})
        for loc in loclist[1:-1]:
            page_url = "https://www.dtsb.com" + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            phone = (
                soup.findAll("div", {"class": "et_pb_blurb_description"})[1]
                .get_text(separator="|", strip=True)
                .split("|")[1]
            )
            temp = r.text.split(' "@graph": ')[1].split("}</script>")[0]
            temp = json.loads(temp)
            address = temp[0]["address"]
            geo = temp[0]["geo"]
            location_name = address["name"].replace(" &amp;", " ")
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            country_code = address["addressCountry"]
            latitude = geo["latitude"]
            longitude = geo["longitude"]
            hours_of_operation = (
                temp[-5]["dayOfWeek"]
                + " "
                + temp[-5]["opens"]
                + "-"
                + temp[-5]["closes"]
                + " "
                + temp[-4]["dayOfWeek"]
                + " "
                + temp[-4]["opens"]
                + "-"
                + temp[-4]["closes"]
                + " "
                + temp[-3]["dayOfWeek"]
                + " "
                + temp[-3]["opens"]
                + "-"
                + temp[-3]["closes"]
                + " "
                + temp[-2]["dayOfWeek"]
                + " "
                + temp[-2]["opens"]
                + "-"
                + temp[-2]["closes"]
                + " "
                + temp[-1]["dayOfWeek"]
                + " "
                + temp[-1]["opens"]
                + "-"
                + temp[-1]["closes"]
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
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
