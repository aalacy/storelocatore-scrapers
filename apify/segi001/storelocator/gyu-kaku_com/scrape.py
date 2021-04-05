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
    locator_domain = "https://www.gyu-kaku.com/"

    sess = sgrequests.SgRequests()

    req = sess.get("https://www.gyu-kaku.com/locations-menus-2/").text

    soup = bs4.BeautifulSoup(req, features="lxml")

    location_slugs = soup.findAll("a", href=True)

    ignore = [
        "https://www.gyu-kaku.com",
        "https://www.gyu-kaku.com/",
        "https://www.gyu-kaku.com/locations-menus-2/",
        "https://www.gyu-kaku.com/reservations/",
        "https://gyukaku.securetree.com/",
        "https://www.gyu-kaku.com/rewards/",
        "https://www.gyu-kaku.com/careers/",
        "https://www.gyu-kaku.com/own-a-gyu-kaku/",
        "https://www.gyu-kaku.com/contact/",
        "https://www.gyu-kaku.com/order/",
        "https://www.facebook.com/gyukakujbbq",
        "https://www.instagram.com/gyukakujbbq/",
        "https://www.gyu-kaku.com/wp-content/uploads/2020/12/coverpage_grandmenu2011.pdf",
        "https://www.gyu-kaku.com/wp-content/uploads/2019/10/guide_nutrition1910.pdf",
        "http://www.gyu-kaku.com/email-newsletter/",
        "https://www.gyu-kaku.com/gift-cards/",
        "https://www.gyu-kaku.com/email-newsletter/",
        "https://www.gyu-kaku.com/careers/",
        "https://www.gyu-kaku.com/own-a-gyu-kaku/",
        "https://www.gyu-kaku.com/privacy-policy/",
        "https://www.gyu-kaku.com/app-terms-and-conditions/",
        "https://www.gyu-kaku.com/site-map/",
        "https://www.gyu-kaku.com/locations-menus/",
        "https://www.gyu-kaku.com/privacy-policy/",
    ]

    missingString = "<MISSING>"

    allSlugs = []

    for s in location_slugs:
        if "/" in s["href"]:
            allSlugs.append(s["href"])

    slugs = [item for item in allSlugs if item not in ignore]

    urls = []

    for slug in slugs:
        url = ""
        if locator_domain in slug or locator_domain.replace("https", "http") in slug:
            url = slug
        else:
            url = "{}{}".format(locator_domain.replace("/", ""), slug)
        if "://" not in url:
            url = url.replace(":", "://")
        urls.append(url)

    def send_crawler(u):
        s = bs4.BeautifulSoup(sgrequests.SgRequests().get(u).text, features="lxml")
        arr = s.find("h4", {"style": "text-align: center;"})
        if "https://www.gyu-kaku.com/new-orleans" in u:
            arr = s.findAll("h4", {"style": "text-align: center;"})[1]
        if arr is None:
            pass
        else:
            mod = arr.text.split("\n")
            name = mod[0]
            if "https://www.gyu-kaku.com/new-orleans" in u:
                name = "NEW ORLEANS".title() + ", LA"
            phone = mod[1]
            street = mod[2].replace(",", "")
            mapsSlug = "https://www.google.com/maps/place/"
            if arr.find("a") is None:
                lat = missingString
                lng = missingString
            else:
                if mapsSlug in arr.find("a")["href"]:
                    latlng = (
                        arr.find("a")["href"]
                        .replace(mapsSlug, "")
                        .split("/")[1]
                        .split(",")
                    )
                    lat = latlng[0].replace("@", "")
                    lng = latlng[1]
                else:
                    lat = missingString
                    lng = missingString
            city = (
                u.replace("https://", "")
                .replace("http://", "")
                .replace("www.gyu-kaku.com/", "")
                .strip()
                .replace("-", " ")
                .replace("/", "")
                .title()
            )
            if "Miami Pinecrest" in city:
                city = "Pinecrest"
            elif "Cambridge Harvard Square" in city:
                city = "Cambridge"
            elif "Chicago" in city:
                city = "Chicago"
            elif "Windward Mall" in city:
                city = "KANEOHE".title()
            elif "Overlandpark" in city:
                city = "Overland Park"
            elif "Houston Memorial" in city:
                city = "Houston"
            elif "Sanfrancisco" in city:
                city = "San Francisco"
            elif "Downtownsandiego" in city:
                city = "San Diego"
            elif "West La" in city:
                city = "LOS ANGELES".title()
            elif "Vancouver Broadway" in city:
                city = "Vancouver"
            elif "Southbay" in city:
                city = "Dorchester"
            if "NYC" in name:
                city = "New York"
            state = name.split(",")[-1].strip()
            zp = mod[-1].strip()
            if "(Entrance on S. Washington St.)" in zp:
                zp = mod[-2].strip()
            elif "(720) 726-4068" in zp:
                zp = mod[-2].strip()
            if len(zp.split(",")) == 4:
                zp = zp.split(",")[2]
            elif len(zp.split(",")) == 3:
                if "BC V5Z 1K7" in zp.split(",")[1]:
                    zp = "V5Z 1K7"
                elif "on l5b 3c3" in zp.split(",")[1]:
                    zp = "l5b 3c3"
                else:
                    zp = zp.split(",")[-1]
            elif len(zp.split(",")[1].strip().split(" ")) == 2:
                zp = zp.split(",")[1].strip().split(" ")[-1]
            elif len(zp.split(",")[1].strip().split(" ")) == 3:
                zp = (
                    zp.split(",")[1].strip().split(" ")[-2]
                    + " "
                    + zp.split(",")[1].strip().split(" ")[-1]
                )
            if "t5j 1Z3" in zp:
                zp = "t5j 1Z3"
            elif "SUGAR LAND, TX 77478" in zp:
                zp = "77478"
            elif "Rancho Cucamonga, CA 91739" in zp:
                zp = "91739"
            hours = missingString
            p = s.findAll("p", {"style": "text-align: center;"})[1].text
            if "AM" in p:
                timeArr = []
                for el in p.strip().replace("(last seating)", "").split("\n"):
                    if "HAPPY HOUR" in el:
                        pass
                    else:
                        timeArr.append(el)
                if "https://www.gyu-kaku.com/bellevue/" in u:
                    hours = " ".join(timeArr).replace(",", "")
                else:
                    hours = ", ".join(timeArr)
            elif "COVID-19" in p:
                p1 = s.findAll("p", {"style": "text-align: center;"})
                timeArr = []
                if len(p1) < 3:
                    hours = missingString
                else:
                    if "This location is currently closed" in p1[2].text:
                        hours = missingString
                    else:
                        for el in (
                            p1[2].text.strip().replace("(last seating)", "").split("\n")
                        ):
                            if "HAPPY HOUR" in el:
                                pass
                            else:
                                timeArr.append(el)
                        hours = ", ".join(timeArr)
            hours = (
                hours.replace(", & 8PM–Close, Monday & Thursday All Day", "")
                .replace("(last order)", "")
                .replace(
                    ", Reservations Required, Limited Dine-In Menu, Premium All You Can Eat, *Premium All You Can Eat, is available Mon–Thu All Day Long",
                    "",
                )
                .replace("(Last Seating)", "")
                .replace("(last seating/order)", "")
                .replace(", Happy Hour: Every Day 11:30AM–6PM", "")
                .replace(
                    "Reservations Required, À la carte Menu, Lunch Menu , *Lunch menu available Mon–Fri until 3PM, Lunch menu not available, on weekends or holidays., Drink Menu, Kid’s Menu, Dessert Menu",
                    "SUN–THU: 11:30AM–9:30PM, FRI & SAT: 11:30AM–10:30PM ",
                )
                .replace("(Last Order)", "")
            )
            if "À la carte Menu" in hours:
                hours = "SUN–THU: 11:30AM–9:30PM, FRI & SAT: 11:30AM–10:30PM "
            typ = missingString
            if hours == "":
                hours = missingString
            if missingString in hours:
                typ = "currently closed".title()
            if "Rancho Cucamonga" in zp:
                zp = "91739"
            if "SUGAR LAND" in zp:
                zp = "77478"
            return [
                locator_domain,
                u,
                name,
                street,
                city,
                state,
                zp,
                missingString,
                missingString,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]

    result = []

    for u in urls:
        lst = send_crawler(u)
        cal = "https://www.gyu-kaku.com/calgary"
        b = bs4.BeautifulSoup(sgrequests.SgRequests().get(cal).text, features="lxml")
        arr = b.find("h3", {"style": "text-align: center;"}).text.strip().split("\n")
        name = arr[0].strip()
        phone = arr[1].strip()
        street = arr[2].strip()
        zp = arr[-1].replace(name, "").strip()
        city = "Calgary"
        state = "AB"
        if lst is None:
            pass
        else:
            result.append(lst)
    result.append(
        [
            locator_domain,
            cal,
            name,
            street,
            city,
            state,
            zp,
            missingString,
            missingString,
            phone,
            "Temporary Closed",
            missingString,
            missingString,
            missingString,
        ]
    )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
