from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://local.gcrtires.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("div", {"id": "contains-place"}).findAll("a")
    for st in statelist:
        stlink = "https://local.gcrtires.com" + st["href"]
        r = session.get(stlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.find("div", {"id": "contains-place"}).findAll("a")
        for div in divlist:
            divlink = "https://local.gcrtires.com" + div["href"]
            r = session.get(divlink, headers=headers)
            loclist = (
                r.text.split('"significantLink": ', 1)[1]
                .split("],", 1)[0]
                .replace("[", "")
                .replace('"', "")
                .split(",")
            )
            for loc in loclist:
                if "-" in loc.split("/")[-2]:
                    pass
                else:
                    continue
                r = session.get(loc, headers=headers)
                content = r.text.split('<script type="application/ld+json">', 1)[
                    1
                ].split("</script", 1)[0]
                content = json.loads(content)

                link = loc
                title = content["name"]
                ccode = content["address"]["addressCountry"]
                city = content["address"]["addressLocality"]
                state = content["address"]["addressRegion"]
                pcode = content["address"]["postalCode"]
                street = content["address"]["streetAddress"]
                lat = content["geo"]["latitude"]
                longt = content["geo"]["longitude"]
                phone = content["telephone"]
                store = content["branchCode"]
                hourslist = content["openingHoursSpecification"]
                hours = ""
                for hr in hourslist:
                    day = hr["dayOfWeek"].split("/")[-1]
                    openstr = hr["opens"] + " AM - "
                    closestr = hr["closes"].split(":", 1)[0]
                    close = int(hr["closes"].split(":", 1)[0])
                    if close > 12:
                        close = close - 12
                    closestr = str(close) + ":" + hr["closes"].split(":", 1)[1] + " PM "
                    hours = hours + day + " " + openstr + closestr
                yield SgRecord(
                    locator_domain="https://www.gcrtires.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code=ccode,
                    store_number=str(store),
                    phone=phone.strip(),
                    location_type="<MISSING>",
                    latitude=str(lat),
                    longitude=str(longt),
                    hours_of_operation=hours,
                )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
