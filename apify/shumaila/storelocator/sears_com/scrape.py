from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://www.sears.com/stores.html"
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find("ul", {"class": "shc-search-by-state__list"})
    statelist = mainul.findAll("a")
    for state in statelist:
        if state["href"].find("404") == -1:
            statelink = "https://www.sears.com" + state["href"]

            state1 = state.text
            flag1 = True
            if flag1:
                if True:
                    page1 = session.get(statelink, headers=headers, verify=False)
                    soup1 = BeautifulSoup(page1.text, "html.parser")
                    linklist = soup1.findAll(
                        "li", {"class": "shc-quick-links--store-details__list--stores"}
                    )
                    for blinks in linklist:
                        link = blinks.find("a")["href"]
                        state1 = blinks.find("a").text.split(",")[1].split("\n", 1)[0]
                        if (
                            link.find("http") == -1
                            and blinks.text.find("Sears Store") > -1
                        ):
                            link = "https://www.sears.com" + link

                            if True:

                                page2 = session.get(link, headers=headers)
                                if True:

                                    if page2.url.find("closed") > -1:
                                        break
                                    else:

                                        soup2 = BeautifulSoup(page2.text, "html.parser")

                                        try:
                                            title = (
                                                soup2.find(
                                                    "h1",
                                                    {"class": "shc-save-store__title"},
                                                )["data-store-title"]
                                                + soup2.find(
                                                    "h1",
                                                    {"class": "shc-save-store__title"},
                                                )["data-unit-number"]
                                            )
                                        except:

                                            title = soup2.find(
                                                "small", {"itemprop": "name"}
                                            ).text
                                        title = title.replace("\n", " ").replace(
                                            "000", " # "
                                        )
                                        title = re.sub(pattern, " ", title)
                                        start = title.find("#")
                                        if start != -1:
                                            store = title.split("#", 1)[1].lstrip()
                                        else:
                                            store = "<MISSING>"
                                        try:
                                            street = (
                                                soup2.find(
                                                    "p",
                                                    {
                                                        "class": "shc-store-location__details--address"
                                                    },
                                                )
                                                .findAll("span")[0]
                                                .text
                                            )
                                            street = street.lstrip()
                                        except:
                                            street = "<MISSING>"
                                        try:
                                            city = (
                                                soup2.find(
                                                    "p",
                                                    {
                                                        "class": "shc-store-location__details--address"
                                                    },
                                                )
                                                .findAll("span")[1]
                                                .text.split(", ")[0]
                                            )
                                            city = city.lstrip()
                                        except:
                                            city = "<MISSING>"
                                        pcode = "<MISSING>"
                                        try:
                                            pcode = (
                                                soup2.find(
                                                    "p",
                                                    {
                                                        "class": "shc-store-location__details--address"
                                                    },
                                                )
                                                .findAll("span")[1]
                                                .text.split(", ")[1]
                                            )
                                        except:
                                            state = "<MISSING>"
                                        try:
                                            phone = soup2.find(
                                                "strong",
                                                {
                                                    "class": "shc-store-location__details--tel"
                                                },
                                            ).text
                                        except:
                                            phone = "<MISSING>"
                                        try:
                                            hourd = soup2.find(
                                                "div",
                                                {"class": "shc-store-hours__details"},
                                            ).findAll("li")
                                            hours = ""
                                            for hour in hourd:

                                                hours = hours + hour.text + " "
                                                hours = re.sub(pattern, " ", hours)
                                        except:
                                            hours = "<MISSING>"
                                        try:
                                            coord = soup2.find(
                                                "div", {"class": "shc-store-location"}
                                            )
                                            lat = coord["data-latitude"]
                                            longt = coord["data-longitude"]
                                        except:
                                            lat = "<MISSING>"
                                            longt = "<MISSING>"
                                        hours = hours.replace("\n", " ")
                                        hours = hours.strip()
                                        title = title.lstrip()
                                        title = title.encode("ascii", "ignore").decode(
                                            "ascii"
                                        )
                                        title = title.replace("Sears", "Sears ")
                                        title = title.replace("  ", " ")

                                        if (
                                            title.lower().find(
                                                "find your next closest Store"
                                            )
                                            == -1
                                        ):

                                            yield SgRecord(
                                                locator_domain="https://www.sears.com/",
                                                page_url=link,
                                                location_name=title,
                                                street_address=street.strip(),
                                                city=city.strip(),
                                                state=state1.strip(),
                                                zip_postal=pcode.strip(),
                                                country_code="US",
                                                store_number=store,
                                                phone=phone.strip(),
                                                location_type="<MISSING>",
                                                latitude=lat,
                                                longitude=longt,
                                                hours_of_operation=hours,
                                            )
                    flag1 = False


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
