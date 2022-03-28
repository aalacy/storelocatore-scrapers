from bs4 import BeautifulSoup
import json
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

    titlelist = []
    for i in range(1, 7):
        statelink = "https://www.extraspace.com/sitemap-" + str(i) + ".aspx"
        try:
            r1 = session.get(statelink, headers=headers)
        except:
            pass
        soup1 = BeautifulSoup(r1.text, "html.parser")
        maindiv1 = soup1.find("div", {"id": "acc-main"})
        link_list = maindiv1.findAll("a")
        for alink in link_list:
            if alink.text.find("Extra Space Storage #") > -1:
                link = "https://www.extraspace.com" + alink["href"]

                r2 = session.get(link, headers=headers)
                try:
                    content = r2.text.split(' "@type": "SelfStorage",', 1)[1].split(
                        "</script>"
                    )[0]
                    content = "{" + content
                    content = json.loads(content)
                except:
                    continue
                city = content["address"]["addressLocality"]
                state = content["address"]["addressRegion"]
                pcode = content["address"]["postalCode"]
                street = content["address"]["streetAddress"]
                title = content["name"]
                phone = content["telephone"].replace("+1-", "")
                lat = content["geo"]["latitude"]
                longt = content["geo"]["longitude"]
                try:
                    hourslist = (
                        BeautifulSoup(r2.text, "html.parser")
                        .text.split("Storage Office Hours", 1)[1]
                        .splitlines()[0:10]
                    )
                except:
                    if "COMING SOON" in BeautifulSoup(r2.text, "html.parser").text:
                        continue
                hours = ""
                for hr in hourslist:
                    if ("am" in hr and "pm" in hr) or "closed" in hr:
                        hours = hours + hr + " "
                    elif hr == " ":
                        break
                hours = (
                    hours.replace("am", " am ")
                    .replace("pm", " pm ")
                    .replace("-", " - ")
                )
                try:
                    hours = hours.split("CUT THE LIN", 1)[0].strip()
                except:
                    pass
                try:
                    hours = hours.split("closed", 1)[0]
                    hours = hours + "closed"
                except:
                    pass
                store = link.split("/")[-2]

                if street in titlelist:
                    continue
                titlelist.append(street)

                yield SgRecord(
                    locator_domain="https://www.extraspace.com",
                    page_url=link,
                    location_name=title.replace("?", ""),
                    street_address=street.replace("<br />", " ").strip(),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
