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
    statelist = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "DC",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
        "Rhodes Island",
    ]
    titlelist = []

    for st in statelist:
        statelink = (
            "https://www.extraspace.com/sitemap/states/"
            + st.lower().replace(" ", "-").strip()
        )

        try:
            r1 = session.get(statelink, headers=headers)
        except:
            pass
        try:
            soup1 = BeautifulSoup(r1.text, "html.parser")
        except:
            continue
        link_list = soup1.select("a[href*=facilities]")

        for alink in link_list:

            if alink["href"].split("/")[-2].isdigit():
                link = "https://www.extraspace.com" + alink["href"]

                try:
                    r2 = session.get(link, headers=headers)

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
