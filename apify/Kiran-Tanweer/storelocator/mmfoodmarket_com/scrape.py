from bs4 import BeautifulSoup
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    session = SgRequests()
    linklist = []
    token = session.get(
        "https://mmfoodmarket.com/en/current_user.json", headers=headers
    ).json()["csrf_token"]

    zips = static_zipcode_list(radius=10, country_code=SearchableCountries.CANADA)

    p = 1
    for zip_code in zips:

        url = (
            "https://mmfoodmarket.com/en/store_locations?utf8=%E2%9C%93&address="
            + zip_code
            + "&button=search&authenticity_token="
            + str(token)
        )
        if p / 50 == 0:
            session = SgRequests()
            token = session.get(
                "https://mmfoodmarket.com/en/current_user.json", headers=headers
            ).json()["csrf_token"]
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "store"})
        for loc in loclist:
            title = loc.find("h3").text
            link = "https://mmfoodmarket.com" + loc.find("h3").find("a")["href"]
            store = link.split("/")[-1]

            try:
                phone = loc.select_one("a[href*=tel]").text
            except:
                phone = "<MISSING>"
            if link in linklist:
                continue
            linklist.append(link)
            try:
                r = session.get(link, headers=headers)
                p = p + 1
                soup = BeautifulSoup(r.text, "html.parser")
                hours = ""
                hourslist = soup.findAll("p", {"class": "store-hours__day"})
                for hr in hourslist:
                    try:
                        hours = (
                            hours
                            + hr.findAll("span")[0].text
                            + " "
                            + hr.findAll("span")[1].text
                            + " "
                        )
                    except:
                        pass
                longt, lat = (
                    r.text.split("coordinates", 1)[1]
                    .split("[", 1)[1]
                    .split("]", 1)[0]
                    .split(",", 1)
                )
                street = r.text.split('"streetAddress":"', 1)[1].split('"', 1)[0]
                city = r.text.split('"addressLocality":"', 1)[1].split('"', 1)[0]
                state = r.text.split('"addressRegion":"', 1)[1].split('"', 1)[0]
                pstr = "+" + state + "+"
                pcode = r.text.split(pstr, 1)[1].split('"', 1)[0].replace("+", " ")
            except:
                continue
            yield SgRecord(
                locator_domain="https://mmfoodmarket.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="CA",
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
