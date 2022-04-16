import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    titlelist = []
    zips = static_zipcode_list(radius=70, country_code=SearchableCountries.USA)
    for zip_code in zips:
        url = "https://www.gerbes.com/atlas/v1/stores/v1/search?filter.query=" + str(
            zip_code
        )

        try:
            loclist = session.get(url, headers=headers).json()["data"]["storeSearch"][
                "results"
            ]
        except:
            continue
        for loc in loclist:

            street = loc["address"]["address"]["addressLines"][0]
            city = loc["address"]["address"]["cityTown"]
            title = loc["address"]["address"]["name"]
            pcode = loc["address"]["address"]["postalCode"]
            state = loc["address"]["address"]["stateProvince"]
            ccode = loc["address"]["address"]["countryCode"]
            lat, longt = (
                str(loc).split("'latLong': '", 1)[1].split("'", 1)[0].split(",")
            )

            store = str(loc).split("'locationId': '", 1)[1].split("'", 1)[0]

            if store in titlelist:
                continue
            titlelist.append(store)
            try:
                hourslist = (
                    str(loc).split("'formattedHours': ", 1)[1].split("],", 1)[0] + "]"
                )
                hourslist = (
                    hourslist.replace("'", '"')
                    .replace("True", '"True"')
                    .replace("False", '"False"')
                )
                hourslist = json.loads(hourslist.replace("'", '"'))
                hourslist = hourslist[0]
                hours = hourslist["displayName"] + " " + hourslist["displayHours"]
            except:

                hours = "<MISSING>"
            ltype = loc["banner"]

            locno = str(loc).split("'storeNumber': '", 1)[1].split("'", 1)[0]
            divid = str(store).replace(str(locno), "")

            try:
                phone = str(loc).split("'phoneNumber': '", 1)[1].split("'", 1)[0]
                phone = "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:]
            except:
                phone = "<MISSING>"
            link = (
                "https://www.gerbes.com/stores/grocery/"
                + str(state.lower())
                + "/"
                + city.lower()
                + "/"
                + title.lower().strip().replace(" ", "-")
                + "/"
                + str(divid)
                + "/"
                + str(locno)
            )

            yield SgRecord(
                locator_domain="https://www.gerbes.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=str(state),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=ltype,
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
