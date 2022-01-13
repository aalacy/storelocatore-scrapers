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

    url = "https://cdn.cookielaw.org/consent/cff990b9-1f4a-4f22-a00f-1deb6e079191/ee12dbc2-52d9-4feb-b90b-58eba69be1e3/fr-fr.json"
    loclist = session.get(url, headers=headers).json()["DomainData"]["Groups"][2][
        "FirstPartyCookies"
    ]

    for loc in loclist:

        link = "https://" + loc["Host"] + "/en-us/"
        print(link)

        if "locale_" in loc["Name"]:
            pass
        else:
            continue
        store = loc["Name"].replace("locale_", "")
        r = session.get(link, headers=headers)
        content = r.text.split('<script type="application/ld+json">', 1)[1].split(
            "</script", 1
        )[0]

        try:
            content = (json.loads(content))["mainEntity"][0]["mainEntity"]
        except:
            continue
        title = content["name"]
        street = content["address"]["streetAddress"]
        city = content["address"]["addressLocality"]
        pcode = content["address"]["postalCode"]
        ccode = content["address"]["addressCountry"]
        phone = content["telephone"]
        lat, longt = content["hasMap"].split("=")[-1].split(",")
        hours = str(content["checkinTime"]) + " - " + str(content["checkoutTime"])

        yield SgRecord(
            locator_domain="https://www.kyriad.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=SgRecord.MISSING,
            zip_postal=pcode.strip(),
            country_code=ccode,
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
