from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("westsidepizza_com")


def fetch_data():
    session = SgRequests()
    HEADERS = {
        "authority": "www.westsidepizza.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    }

    locator_domain = "https://www.westsidepizza.com/"
    ext = "locations/"
    r = session.get(locator_domain + ext, headers=HEADERS)

    soup = BeautifulSoup(r.content, "lxml")

    locs = soup.find("div", {"id": "block-narwhal-content"}).find_all(
        "div", {"class": "views-row"}
    )

    for loc in locs:

        page_url = (
            locator_domain[:-1]
            + loc.find("div", {"class": "views-field-view-node"}).find("a")["href"]
        )
        logger.info(page_url)
        r = session.get(page_url, headers=HEADERS)
        if "coming soon" in r.text.lower():
            continue
        soup = BeautifulSoup(r.content, "lxml")
        store_sel = lxml.html.fromstring(r.text)
        if soup.find("div", {"class": "field-address"}).text.strip() == "Coming Soon!":
            continue
        strongs = soup.find_all("strong")
        hours = ""
        for s in strongs:
            if "Store Hours" in s.text:
                hours_ps = s.parent.parent.find_all("p")
                for h in hours_ps[1:]:
                    hours += " ".join(h.text.split()) + "; "

        hours = hours.strip().split("; ; ")[0].strip()
        if len(hours) > 0 and hours[-1] == ";":
            hours = "".join(hours[:-1]).strip()

        if len(hours) <= 0:
            temp_hours = store_sel.xpath(
                '//div[@class="body"][./p[contains(text(),"Monday")]]/p'
            )
            hours_list = []
            for hour in temp_hours:
                if len("".join(hour.xpath("text()")).strip()) > 0:
                    if "day" in "".join(hour.xpath("text()")).strip():
                        day = (
                            "".join(hour.xpath("text()"))
                            .strip()
                            .split("day")[0]
                            .strip()
                            + "day"
                        )
                        time = (
                            "".join(hour.xpath("text()"))
                            .strip()
                            .split("day")[1]
                            .strip()
                        )
                        hours_list.append(day + " " + time)

            hours = "; ".join(hours_list).strip().split("; There")[0].strip()

        street_address = soup.find("div", {"class": "field-address"}).text
        city = soup.find("div", {"class": "field-city"}).text
        state = soup.find("div", {"class": "field-state"}).text
        zip_code = soup.find("div", {"class": "field-zip-code"}).text

        location_name = soup.find("h1", {"class": "title"}).text.strip()
        try:
            phone_number = soup.find("div", {"class": "field-phone"}).text
        except:
            phone_number = "<MISSING>"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "US"
        lat = "".join(store_sel.xpath('//div[@typeof="Place"]/@data-lat')).strip()
        longit = "".join(store_sel.xpath('//div[@typeof="Place"]/@data-lng')).strip()

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone_number,
            location_type=location_type,
            latitude=lat,
            longitude=longit,
            hours_of_operation=hours,
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
