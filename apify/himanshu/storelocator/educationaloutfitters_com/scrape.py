from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests(verify_ssl=False)
website = "educationaloutfitters.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://educationaloutfitters.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    base_url = "https://www.educationaloutfitters.com"
    r = session.get("http://www.educationaloutfitters.com/states", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    country_code = "US"
    page_url = "http://www.educationaloutfitters.com/states"
    for script in soup.find_all("li", {"class": "navList-item"}):
        r1 = session.get(script.find("a")["href"], headers=headers)
        if not r1:
            continue
        soup1 = BeautifulSoup(r1.text, "lxml")
        for lep in soup1.find_all("article", {"class": "modern__card"}):
            location_name = lep.find("a", {"class": "modern__card-title-link"}).text
            r_location = session.get(lep.find("a")["href"], headers=headers)
            if not r_location:
                continue
            soup_location = BeautifulSoup(r_location.text, "lxml")
            page_url = soup_location.find("div", {"class": "store-button"}).find("a")[
                "href"
            ]
            log.info(page_url)
            hours_of_operation = MISSING
            if (
                "shop.readsuniforms.net/educationnc" not in page_url
                and "toledo.educationaloutfitters.com" not in page_url
            ):
                r4 = session.request(
                    page_url,
                    headers=headers,
                )
                if r4:
                    if r4.status_code == 200:
                        soup5 = BeautifulSoup(r4.text, "lxml")
                        try:
                            hours_of_operation = (
                                " ".join(
                                    list(
                                        soup5.find(
                                            "p", {"class": "basic__hours"}
                                        ).stripped_strings
                                    )
                                )
                                .replace("Customer Service Hours:", "")
                                .replace("Store Hours:", "")
                            )
                        except:
                            hours_of_operation = MISSING

            hours_of_operation = (
                hours_of_operation.replace("WALK INS WELCOME THRU MAY", "")
                .replace("Store Hours for Curb-side Pick-up:", "")
                .replace("REQUIRED APPOINTMENT to shop in store  ", "")
            )
            d = soup_location.find("li", {"class": "store-address"})
            full_detail = list(d.stripped_strings)
            phone = soup_location.find("li", {"class": "store-tel"}).text.strip()
            full_address = full_detail[1:]
            location_name = full_detail[0]
            if len(full_address) == 1:
                street_address = MISSING
                city = full_address[0].split(",")[0]
                state = full_address[0].split(",")[1]
            elif len(full_address) == 2:
                street_address = " ".join(full_address[:-1])
                city = full_address[-1].split(",")[0]
                state = (
                    full_address[-1]
                    .split(",")[-1]
                    .strip()
                    .split()[0]
                    .replace("78213", "TX")
                )
                zipp = full_address[-1].split(",")[-1].strip().split()[-1]

            page_url = lep.find("a")["href"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
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
