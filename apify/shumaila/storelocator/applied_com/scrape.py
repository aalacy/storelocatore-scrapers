from bs4 import BeautifulSoup
import re
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from sgselenium.sgselenium import SgChrome

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():

    streetlist = []
    pattern = re.compile(r"\s\s+")
    urllist = [
        "https://www.applied.com/store-finder/position?country=CA&hideDistances=true",
        "https://www.applied.com/store-finder/position?country=US&hideDistances=true",
    ]
    ccode = "US"
    with SgChrome(user_agent=user_agent) as driver:

        for url in urllist:
            if "country=CA" in url:
                ccode = "CA"
            else:
                ccode = "US"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            storelist = soup.find("table", {"class": "store-list"}).findAll(
                "tr", {"class": "item"}
            )

            coordlist = (
                driver.page_source.split('data-stores="{', 1)[1]
                .split('}"', 1)[0]
                .split("{")[1:]
            )

            for div in storelist:
                tdlist = div.findAll("td")
                col1 = re.sub(pattern, "\n", tdlist[0].text).lstrip().splitlines()
                title = col1[0]
                store = col1[1].replace("(", "").replace(")", "").strip()
                phone = col1[2]
                address = re.sub(pattern, "\n", tdlist[1].text).lstrip().splitlines()
                link = "https://www.applied.com" + tdlist[0].find("a")["href"]
                street = address[0]
                try:
                    city, state = address[1].split(", ", 1)
                except:
                    if address[1].split(",", 1)[0] in link:
                        state = link.split(address[1].split(",", 1)[0] + ", ")[1].split(
                            " ", 1
                        )[0]
                        city = address[1].split(",", 1)[0]
                pcode = address[2]
                if title in streetlist:
                    continue
                streetlist.append(title)

                if "View Map" in phone:
                    phone = "<MISSING>"
                lat = "<MISSING>"
                longt = "<MISSING>"
                for coord in coordlist:
                    coord = (
                        coord.replace("\n", "")
                        .replace("\t", "")
                        .lstrip()
                        .replace("&quot;", '"')
                    )
                    coord = "{" + coord.split("}", 1)[0] + "}"

                    try:

                        coord = json.loads(coord)

                        if title.strip() == coord["name"]:
                            lat = coord["latitude"]
                            longt = coord["longitude"]
                            break
                    except:
                        pass
                if len(str(lat)) < 4:
                    lat = longt = "<MISSING>"
                yield SgRecord(
                    locator_domain="https://www.applied.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code=ccode,
                    store_number=str(store),
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=str(lat),
                    longitude=str(longt),
                    hours_of_operation=SgRecord.MISSING,
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
