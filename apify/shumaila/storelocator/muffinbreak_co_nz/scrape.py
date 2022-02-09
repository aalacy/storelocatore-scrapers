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

    url = "https://muffinbreak.co.nz/wp-json/store-locator/v1/store/?origLat=-40.915496&origLng=175.007312&origAddress=Paraparaumu%205032&formattedAddress=Paraparaumu%2C%20New%20Zealand&boundsNorthEast=%7B%22lat%22%3A-40.8713939%2C%22lng%22%3A175.0545339%7D&boundsSouthWest=%7B%22lat%22%3A-40.973652%2C%22lng%22%3A174.9722803%7D"
    loclist = session.get(url, headers=headers).json()
    for loc in loclist:
        store = loc["id"]
        title = loc["locname"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["address"]
        rawaddr = loc["address"] + " " + loc["address2"]

        city = loc["address2"].replace(", NEW ZEALAND", "")
        if " - " in city:
            temp, city = city.split(" - ", 1)
            street = street + " " + temp
        elif len(city.split(" ")) > 1:
            temp = city.split(" ")[0 : len(city.split(" ")) - 2]
            temp = " ".join(temp[0:])
            if (
                "Mt" in temp
                or "Kapiti" in temp
                or "North" in temp
                or "New" in temp
                or "Palmerston" in temp
            ):

                city = temp + " " + city
            else:

                city = city.split(" ")[len(city.split(" ")) - 2 :]
                city = " ".join(city[0:])
                street = street + " " + temp
        try:
            city, pcode = city.split(" ", 1)
        except:
            pcode = "<MISSING>"
        try:
            if city in pcode:
                city, pcode = pcode.split(", ", 1)
            else:
                temp, pcode = pcode.split(", ", 1)
                city = city + " " + temp
        except:
            pass
        phone = loc["phone"]
        link = loc["web"]
        if "coming-soon" in link:
            continue
        if "muffin-break-invercargill" in link and "<MISSING>" in pcode:
            street = "21 Clyde Street"
            pcode = "9810"
        yield SgRecord(
            locator_domain="https://muffinbreak.co.nz/",
            page_url=link,
            location_name=title,
            street_address=street.replace(",", "").strip(),
            city=city.replace(",", "").strip(),
            state="<MISSING>",
            zip_postal=pcode.replace(",", "").strip(),
            country_code="NZ",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
            raw_address=rawaddr,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
