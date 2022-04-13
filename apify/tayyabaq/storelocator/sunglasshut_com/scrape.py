from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://stores.sunglasshut.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    clist = soup.find("ul", {"class": "Directory-listLinks"}).findAll(
        "a", {"class": "Directory-listLink"}
    )

    for country in clist:
        clink = country["href"]
        try:
            ccode = clink.split("/", 1)[0].upper()
        except:
            ccode = clink
        clink = "https://stores.sunglasshut.com/" + clink

        r = session.get(clink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        check3 = 0
        try:
            statelist = soup.find("section", {"class": "StateList"}).findAll(
                "a", {"class": "Directory-listLink"}
            )
        except:
            statelist = []
            statelist.append(clink)
            check3 = 1
        for stnow in statelist:
            check1 = 0
            if check3 == 0:
                stlink = "https://stores.sunglasshut.com/" + stnow["href"]

                r = session.get(stlink, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
            else:
                stlink = stnow
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
                    citylink = "https://stores.sunglasshut.com/" + citynow["href"]
                    citylink = citylink.replace("../", "")

                    r = session.get(citylink, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                else:
                    branchlist = []
                    branchlist.append(citynow)
                    check2 = 1
                try:
                    branchlist = soup.find(
                        "ul", {"class": "Directory-listTeasers"}
                    ).findAll("a", {"class": "Teaser-titleLink"})

                    check2 = 0
                except:

                    branchlist = []
                    branchlist.append(r.url)
                    check2 = 1
                for branch in branchlist:
                    if check2 == 0:
                        branch = "https://stores.sunglasshut.com/" + branch["href"]
                        branch = branch.replace("../", "")

                        r = session.get(branch, headers=headers)
                        soup = BeautifulSoup(r.text, "html.parser")
                        branch = r.url
                    lat = soup.find("meta", {"itemprop": "latitude"})["content"]
                    longt = soup.find("meta", {"itemprop": "longitude"})["content"]
                    title = (
                        soup.find("h1", {"class": "Core-name"})
                        .text.replace("\n", " ")
                        .strip()
                    )
                    street = soup.find("span", {"class": "c-address-street-1"}).text
                    try:
                        street = (
                            street
                            + " "
                            + soup.find("span", {"class": "c-address-street-2"}).text
                        )
                    except:
                        pass
                    city = soup.find("span", {"class": "c-address-city"}).text
                    try:
                        state = soup.find("abbr", {"class": "c-address-state"}).text
                    except:
                        state = "<MISSING>"
                    pcode = soup.find("span", {"class": "c-address-postal-code"}).text
                    phone = soup.find("div", {"id": "phone-main"}).text
                    try:
                        hours = (
                            soup.find("table", {"class": "c-hours-details"})
                            .text.replace("PM", "PM ")
                            .replace("day", "day ")
                        )
                        try:
                            hours = hours.split("Week", 1)[1]
                        except:
                            pass
                        try:
                            hours = hours.split("Hours", 1)[1]
                        except:
                            pass
                    except:
                        hours = "Temporarily Closed"
                    branch = r.url
                    yield SgRecord(
                        locator_domain="https://www.sunglasshut.com",
                        page_url=branch,
                        location_name=title,
                        street_address=street.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=pcode.strip(),
                        country_code=ccode,
                        store_number=SgRecord.MISSING,
                        phone=phone.strip(),
                        location_type=SgRecord.MISSING,
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
