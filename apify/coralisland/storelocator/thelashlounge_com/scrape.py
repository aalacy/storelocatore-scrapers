import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "thelashlounge_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}

DOMAIN = "https://www.thelashlounge.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.thelashlounge.com/salons/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "location-bottom-link"})
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            base = BeautifulSoup(r.text, "html.parser")
            temp = r.text.split("<script type='application/ld+json'> ")[1].split(
                "</script>"
            )[0]
            temp = json.loads(temp)
            location_name = temp["name"]
            try:
                phone = temp["telephone"]
            except:
                phone = base.find(class_="pre-footer-details").a.text.strip()
            address = temp["address"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            street_address = (
                address["streetAddress"]
                .replace("<br/>", "")
                .replace(" </br>", "")
                .replace(city, "")
                .replace(state, "")
                .replace(zip_postal, "")
                .replace("Shoppes at", "")
                .strip()
            )
            country_code = address["addressCountry"]
            latitude = str(temp["geo"]["latitude"])
            longitude = str(temp["geo"]["longitude"])
            if (
                "COMING SOON"
                in base.find_all(class_="home-contact-content")[-1].text.upper()
            ):
                continue
            try:
                if "COMING SOON" in base.find(class_="banner-title").text.upper():
                    continue
            except:
                pass
            hours_of_operation = " ".join(
                list(base.find(class_="hours").stripped_strings)
            )

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
