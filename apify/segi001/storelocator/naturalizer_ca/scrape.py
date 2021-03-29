import csv
import sgrequests
import bs4


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    locator_domain = "https://www.naturalizer.ca/"
    store_sitemap = "https://ecomprdsharedstorage.blob.core.windows.net/sitemaps/70000/stores-sitemap.xml"
    missingString = "<MISSING>"
    future_location = "future-location"

    sess = sgrequests.SgRequests()
    sitemap_request = sess.get(store_sitemap).text

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }

    stores = bs4.BeautifulSoup(sitemap_request, features="lxml").findAll("loc")

    result = []

    for store in stores:
        url = store.text
        if url == "https://www.naturalizer.ca":
            pass
        elif future_location in url:
            pass
        else:
            r = bs4.BeautifulSoup(sess.get(url, headers=headers).text, features="lxml")
            l = r.find("div", {"class": "StoreListResult"})
            name = l.find("h1").text.title()
            address_list = l.findAll("span")
            street = address_list[0].text
            city = address_list[1].text.split(",")[0]
            state = address_list[1].text.split(" ")
            zipc = address_list[1].text.split(" ")
            hours = missingString
            if (
                "SUITE" in city
                or "SPACE" in city
                or "BOX" in city
                or "N.E" in city
                or "STE " in city
                or "RTE" in city
                or "HWY" in city
                or "ROUTE" in city
                or "UNIT" in city
                or "I-35" in city
                or "I4" in city
                or "INTERSTATE" in city
                or "I-5" in city
                or "3525 W CARSON" in city
                or "LOT 414" in city
                or "I95/WHITE MARSH BLVD" in city
                or "FLATBUSH AVE AND AVENUE 'U'" in city
                or "STORE 617" in city
                or "168 FASHION PARK" in city
                or "5001 MONROE STREET" in city
                or "3560 GALLERIA II" in city
                or "601 WABASH ROAD & MICHIGAN BLVD" in city
                or "175 MILLCREEK MALL" in city
                or "LEE ST E & COURT ST" in city
                or "76 EASTLAND S.C." in city
                or "41ST AND BROADWAY" in city
            ):
                street = "{} {}".format(street, city)
                city = address_list[2].text.split(",")[0]
                state = address_list[2].text.split(" ")[-2]
                zipc = address_list[2].text.split(" ")[-1]
            elif state[0] == "COLISEUM/COLDWATER":
                state = address_list[2].text.split(" ")[-2]
                zipc = address_list[2].text.split(" ")[-1]
            elif state[0] == "PARAMOUNT":
                state = address_list[2].text.split(" ")[-2]
                zipc = address_list[2].text.split(" ")[-1]
            else:
                if len(address_list[1].text.split(" ")) > 1:
                    state = address_list[1].text.split(",")[-1].strip().split(" ")[0]
                    zipc = (
                        address_list[1].text.split(" ")[-2]
                        + " "
                        + address_list[1].text.split(" ")[-1]
                    )
                else:
                    state = address_list[2].text.split(",")[-1].strip().split(" ")[0]
                    zipc = (
                        address_list[2].text.split(" ")[-2]
                        + " "
                        + address_list[1].text.split(" ")[-1]
                    )
            store_num = l.find("input")["value"]
            phone = address_list[-1].text
            timeArray = []
            if r.find("strong", {"class": "store-hours"}):
                h = r.findAll("strong", {"class": "store-hours"})
                for hs in h:
                    timeArray.append(
                        " {} : {} ".format(hs["data-day"], hs["data-hours"])
                    )
                hours = ", ".join(timeArray)
            if "PARAMOUNT & PONONA" in city:
                city = "Montebello"
            if "COLISEUM/COLDWATER" in city:
                city = "Ft. Wayne"
            if street == "":
                street = missingString
            if name == "None":
                name = missingString
            if "Galeries St-Hyacinthe" in name:
                city = "Saint-Hyacinthe"
                zipc = "J2S 4Z5"
            if "Cf Markville" in name:
                city = "Markham"
                zipc = "L3R 4M9"
            if "Bramalea CCity Center" in name:
                city = "Brampton"
                zipc = "L6T 3R5"
            if "Mcarthurglen Vancouver" in name:
                state = "BC"
                zipc = "V7B 0B7"
            if "Outlet Collection Winnipeg" in name:
                city = "Winnipeg"
                zipc = "R3P 2T3"
                state = "MB"
            if "Metropolis At Metrotown" in name:
                city = "Burnaby"
            result.append(
                [
                    locator_domain,
                    url,
                    name,
                    street,
                    city,
                    state,
                    zipc,
                    missingString,
                    store_num,
                    phone,
                    missingString,
                    missingString,
                    missingString,
                    hours,
                ]
            )

    m_set = set()

    res = []

    for sb in result:
        se = sb[2]
        if se not in m_set:
            res.append(sb)
            m_set.add(se)

    return res


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
