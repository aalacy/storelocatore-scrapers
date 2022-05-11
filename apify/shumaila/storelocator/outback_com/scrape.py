from bs4 import BeautifulSoup
import re
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


MISSING = SgRecord.MISSING


def fetch_data():

    pattern = re.compile(r"\s\s+")
    url = "https://www.outback.com/locations/international"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.findAll("ul", {"class": "directory-listing"})

    for cnow in statelist:
        ccode = cnow["ng-show"].split("'", 1)[1].split("'", 1)[0]
        loclist = cnow.findAll("li", {"class": "directory-listing-entry"})
        for loc in loclist:
            loc = re.sub(pattern, "\n", loc.text).strip()
            title = loc.split("\n", 1)[0]

            address = loc.split("Address", 1)[1].split("WiFi", 1)[0].strip()
            phone = address.split("\n")[-1]

            address = address.replace(phone, "")
            raw_address = address.replace("\n", " ").strip()
            hours = "<MISSING>"
            lat = longt = "<MISSING>"
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            pcode = zip_postal.strip() if zip_postal else MISSING
            if "Address" in title:
                title = raw_address
            pcode = pcode.replace("CEP ", "").replace("-DONG", "").replace("-GA", "")
            yield SgRecord(
                locator_domain="https://www.outback.com/",
                page_url="<MISSING>",
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude="<MISSING>",
                hours_of_operation=hours,
                raw_address=raw_address,
            )
    session1 = SgRequests()
    url = "https://locations.outback.com/index.html"
    r = session1.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("section", {"class": "StateList"}).findAll(
        "a", {"class": "Directory-listLink"}
    )

    for stnow in statelist:
        check1 = 0
        stlink = "https://locations.outback.com/" + stnow["href"]
        r = session1.get(stlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            citylist = soup.find("section", {"class": "CityList"}).findAll(
                "a", {"class": "Directory-listLink"}
            )
        except:
            citylist = []
            citylist.append(stlink)
            check1 = 1
        for citynow in citylist:
            check2 = 0
            if check1 == 0:
                citylink = "https://locations.outback.com/" + citynow["href"]
                r = session1.get(citylink, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    branchlist = soup.find(
                        "ul", {"class": "Directory-listTeasers"}
                    ).findAll("a", {"class": "Teaser-titleLink"})
                except:
                    branchlist = []
                    branchlist.append(citylink)
                    check2 = 1
            else:
                branchlist = []
                branchlist.append(citylink)
                check2 = 1
            for branch in branchlist:
                if check2 == 0:
                    branch = "https://locations.outback.com/" + branch["href"]
                    branch = branch.replace("../", "")

                    r = session1.get(branch, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                store = r.text.split('"storeId":"', 1)[1].split('"', 1)[0]
                try:
                    lat = r.text.split('"latitude":', 1)[1].split(",", 1)[0]
                    longt = r.text.split('"longitude":', 1)[1].split("}", 1)[0]
                except:
                    lat = longt = "<MISSING>"
                try:

                    title = (
                        soup.find("h1", {"id": "location-name"})
                        .text.replace("\n", " ")
                        .strip()
                    )
                except:
                    try:
                        title = soup.find("h1").text.replace("\n", " ").strip()
                    except:
                        continue
                street = soup.find("span", {"class": "c-address-street-1"}).text
                city = soup.find("span", {"class": "c-address-city"}).text
                try:
                    state = soup.find("abbr", {"class": "c-address-state"}).text
                except:
                    continue
                pcode = soup.find("span", {"class": "c-address-postal-code"}).text
                try:
                    phone = soup.find("div", {"id": "phone-main"}).text
                except:
                    phone = "<MISSING>"
                hours = soup.find("table", {"class": "c-hours-details"}).text.replace(
                    "PM", "PM "
                )
                try:
                    hours = hours.split("Week", 1)[1]
                except:
                    pass
                try:
                    hours = hours.split("Hours", 1)[1]
                except:
                    pass
                hours = hours.replace("day", "day ").replace("osed", "osed ").strip()

                yield SgRecord(
                    locator_domain="https://www.outback.com/",
                    page_url=branch,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=str(store),
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=str(lat),
                    longitude=str(longt),
                    hours_of_operation=hours,
                )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=5,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
