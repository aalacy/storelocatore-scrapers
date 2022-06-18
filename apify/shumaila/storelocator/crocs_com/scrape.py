from sgrequests import SgRequests
import json
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import unidecode

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

checklist = []


def fetch_data():

    mylist = DynamicGeoSearch(country_codes=SearchableCountries.ALL)

    for lat, lng in mylist:

        url = (
            "https://crocs.locally.com/stores/conversion_data?has_data=true&company_id=1762&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat="
            + str(lat)
            + "&map_center_lng="
            + str(lng)
            + "&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=6.727111799313498&lang=en-us"
        )

        try:
            loclist = session.get(url, headers=headers).json()["markers"]

        except:
            continue

        for loc in loclist:

            store = loc["id"]
            title = loc["name"]
            lat = loc["lat"]
            longt = loc["lng"]
            street = loc["address"]
            state = loc["state"]
            city = loc["city"]
            pcode = loc["zip"]
            phone = loc["phone"]
            ccode = loc["country"]
            hours = ""
            ltype = "Store"
            if len(loc["slug"].strip()) > 5:
                link = "https://locations.crocs.com/shop/" + loc["slug"].strip()

                if link in checklist:
                    pass
                else:
                    checklist.append(link)
                    ltype = "Store"
                    r = session.get(link, headers=headers)
                    try:
                        hourslist = (
                            "["
                            + r.text.split('"openingHoursSpecification":[', 1)[1].split(
                                "],", 1
                            )[0]
                            + "]"
                        )
                        hourslist = json.loads(hourslist)
                    except:
                        try:
                            hourslist = (
                                "["
                                + r.text.split('"openingHoursSpecification":[', 1)[1]
                                .split("</script>", 1)[0]
                                .strip()
                            )
                            hourslist = hourslist.replace("}]}", "}]")
                            hourslist = json.loads(hourslist)
                        except:
                            hourslist = []

                    for hr in hourslist:
                        try:
                            for day in hr["dayOfWeek"]:
                                hours = (
                                    hours
                                    + day
                                    + " "
                                    + hr["opens"]
                                    + "-"
                                    + hr["closes"]
                                    + " "
                                )
                        except:
                            pass

            else:
                ltype = "Dealer"
                link = "<MISSING>"
            hours = ""

            if len(hours) < 3:
                hours = "<MISSING>"
            if state.isdigit():
                state = "<MISSING>"

            yield SgRecord(
                locator_domain="https://www.crocs.com/",
                page_url=link,
                location_name=unidecode.unidecode(title),
                street_address=unidecode.unidecode(street).strip(),
                city=unidecode.unidecode(city).strip(),
                state=state.strip(),
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
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
