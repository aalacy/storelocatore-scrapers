from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = SgLogSetup().get_logger("industriousoffice_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    titlelist = []
    titlelist.append("none")
    url = "https://www.industriousoffice.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    state_list = soup.find(
        "section", {"class": "section-all-locations-v2 my-lg"}
    ).findAll("li", {"class": "market"})
    p = 0
    for states in state_list:
        states = states.find("a")["href"]
        log.info(states)
        rr = session.get(states, headers=headers, verify=False)

        try:
            r = rr.text.split("var marketLocations = ", 1)[1].split("];", 1)[0]
            loclist = json.loads(r + "]")
            for loc in loclist:

                city = loc["city"]
                state = loc["abbr"]
                pcode = loc["zip"]
                phone = loc["phone"]
                street = loc["address"]
                title = loc["location_title"]
                lat = loc["latitude"]
                longt = loc["longitude"]
                status = loc["text_status"]
                if status:
                    if status.find("Coming") > -1 or status.find("Opening") > -1:
                        continue
                link = loc["permalink"].replace("\\", "")
                if state == "Wisconsin":
                    state = "WI"
                try:
                    if len(state) < 2:
                        state = loc["state"]
                except:
                    state = loc["state"]

                country_code = "US"
                try:
                    country_code = loc["country"]
                except:
                    pass

                if country_code == "UK":
                    state = "<MISSING>"

                if phone != "" and title not in titlelist:
                    titlelist.append(title)

                    yield SgRecord(
                        locator_domain="https://www.industriousoffice.com/",
                        page_url=link,
                        location_name=title,
                        street_address=street,
                        city=city,
                        state=state,
                        zip_postal=pcode,
                        country_code=country_code,
                        store_number="<MISSING>",
                        phone=phone,
                        location_type="<MISSING>",
                        latitude=lat,
                        longitude=longt,
                        hours_of_operation="<MISSING>",
                    )
                    p += 1

        except:

            r = rr.text.split('<script type="application/ld+json">', 1)[1].split(
                "</script>", 1
            )[0]
            r = json.loads(r)
            link = states
            title = r["name"]
            phone = r["telephone"]
            street = r["address"]["streetAddress"]
            city = r["address"]["addressLocality"]
            state = r["address"]["addressRegion"]
            pcode = r["address"]["postalCode"]
            lat = r["geo"]["latitude"]
            longt = r["geo"]["longitude"]
            if state == "Wisconsin":
                state = "WI"
            if phone != "" and title not in titlelist:
                titlelist.append(title)
                yield SgRecord(
                    locator_domain="https://www.industriousoffice.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street,
                    city=city,
                    state=state,
                    zip_postal=pcode,
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=lat,
                    longitude=longt,
                    hours_of_operation="<MISSING>",
                )
                p += 1


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
