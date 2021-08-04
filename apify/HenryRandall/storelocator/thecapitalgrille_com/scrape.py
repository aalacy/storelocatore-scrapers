import json
from sgselenium import SgSelenium
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }
    driver = SgSelenium().chrome()

    locator_domain = "https://www.thecapitalgrille.com/home"
    url = "https://www.thecapitalgrille.com/locations-sitemap.xml"
    session = SgRequests()
    r = session.get(url, headers=headers, verify=False)
    loc_list = []
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "href" in line:
            loc_list.append(line.split('href="', 1)[1].split('"', 1)[0])

    for loc in loc_list:
        if "mexico" not in loc:
            driver.get(loc)
            soup = bs(driver.page_source, "html.parser")
            metadata = soup.find("script", {"type": "application/ld+json"})
            metadata = json.loads(str(metadata).split("\n")[1].split("</")[0])
            address = metadata["address"]
            country = address["addressCountry"]
            street = address["streetAddress"]
            zip_code = address["postalCode"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            phone = metadata["telephone"]
            storeID = metadata["branchCode"]
            coords = metadata["geo"]
            lat = coords["latitude"]
            long = coords["longitude"]
            storename = metadata["name"]
            times = soup.find_all("span", {"class": "time-holder rolling-time"})
            today = soup.find(
                "span", {"class": "day-holder capitalize text-center rolling-width"}
            )
            otherdays = soup.find_all(
                "span", {"class": "day-holder capitalize text-center rolling-day-width"}
            )

            time = (
                times[0].text.strip().replace("\n\n\xa0", " ").replace("\xa0\n\n", " ")
            )
            day = today.text.strip().split("(")[1].split(")")[0]
            hoo = day + " " + time + ", "
            for x in range(len(otherdays)):
                time = (
                    times[x + 1]
                    .text.strip()
                    .replace("\n\n\xa0", " ")
                    .replace("\xa0\n\n", " ")
                )
                day = otherdays[x].text.strip()
                hoo = hoo + day + " " + time + ", "
            hoo = hoo[:-2]
            location_type = SgRecord.MISSING

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=loc,
                    location_name=storename,
                    street_address=street,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country,
                    store_number=storeID,
                    phone=phone,
                    location_type=location_type,
                    latitude=lat,
                    longitude=long,
                    hours_of_operation=hoo,
                )
            )


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)


scrape()
