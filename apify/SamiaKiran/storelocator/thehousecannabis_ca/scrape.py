import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "thehousecannabis_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://thehousecannabis.ca"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://thehousecannabis.ca/stores/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=location]")
        page_list = []
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            page_url = page_url.strip("/")
            if page_url in page_list:
                continue
            page_list.append(page_url)
            r = session.get(page_url, headers=headers)
            if r.status_code == 200:
                log.info(page_url)
                soup = BeautifulSoup(r.text, "html.parser")
                temp_street = soup.find("h3").text
                schema = r.text.split(
                    '<script data-react-helmet="true" type="application/ld+json">'
                )[1].split("</script>", 1)[0]
                schema = schema.replace("\n", "")
                loc = json.loads(schema)
                address = loc["address"]
                country_code = address["addressCountry"]
                street_address = address["streetAddress"]
                if temp_street.split()[0] == street_address.split()[0]:
                    street_address = address["streetAddress"]
                    latitude = loc["geo"]["latitude"]
                    longitude = loc["geo"]["longitude"]
                    city = address["addressLocality"]
                    state = address["addressRegion"]
                    zip_postal = address["postalCode"]
                else:
                    street_address = soup.find("h3").text
                    latitude = MISSING
                    longitude = MISSING
                    city = page_url.split("/")[-2]
                    state = MISSING
                    zip_postal = MISSING
                location_name = "House of Cannabis " + city
                phone = soup.select_one("a[href*=tel]").text
                try:
                    temp_list = r.text.split("MONDAY")[1].split("Order Online")[0]
                except:
                    temp_list = r.text.split("Monday")[1].split("Order Online")[0]
                temp_list = "MONDAY " + BeautifulSoup(
                    temp_list, "html.parser"
                ).get_text(separator="|", strip=True).replace("|", " ")
                temp_list = (
                    temp_list.replace("SUNDAY", "SUNSAY#")
                    .replace(" - ", "-")
                    .split("#")
                )
                day_list = temp_list[0].split()
                time_list = temp_list[1].split()
                hours_of_operation = ""
                for day, time in zip(day_list, time_list):
                    hours_of_operation = hours_of_operation + " " + day + " " + time
                hours_of_operation = hours_of_operation.lower()
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
