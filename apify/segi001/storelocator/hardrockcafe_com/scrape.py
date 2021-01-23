import csv
import sgrequests
import bs4
import re
import json


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
    locator_domain = "https://www.hardrockcafe.com/"

    missingString = "<MISSING>"

    slugs = ["UNITED STATES", "CANADA", "ENGLAND", "SCOTLAND"]

    store_urls = []

    def getStores(slug, arr):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
        }
        sess = sgrequests.SgRequests().get(
            "https://www.hardrockcafe.com/locations.aspx", headers=headers
        )
        s = bs4.BeautifulSoup(sess.text, features="lxml")
        divs = s.findAll("div")
        for div in divs:
            if div.find("h4"):
                if slug in div.find("h4"):
                    a = div.findAll("a", href=True)
                    for ass in a:
                        arr.append(ass["href"])

    getStores(slugs[0], store_urls)
    getStores(slugs[1], store_urls)
    getStores(slugs[2], store_urls)
    getStores(slugs[3], store_urls)

    con = set(store_urls)

    def generateSoup(link):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
        }
        txt = sgrequests.SgRequests().get(link, headers=headers).text
        return [txt, bs4.BeautifulSoup(txt, features="lxml")]

    result = []

    yext_id = []

    for st in con:
        ss = generateSoup(st)
        s = ss[1]
        ld = json.loads(
            str(s.find("script", {"type": "application/ld+json"}))
            .replace('<script type="application/ld+json">', "")
            .replace("</script>", "")
        )
        url = ld["url"]
        name = ld["name"]
        loc_type = ld["@type"]
        country = None
        if "addressCountry" in ld["address"]:
            country = ld["address"]["addressCountry"]
        sess = (
            sgrequests.SgRequests()
            .get("https://www.hardrockcafe.com/locations.aspx")
            .text
        )
        r = re.findall(r"var currentMapPoint=(.*?)}", sess)
        for rs in r:
            n = re.search(r'<span class="moreInfoLink"><a href="(.*?)">', rs).group(1)
            yext = re.search(r''''yextEntityId':"(.*?)"''', rs).group(1)
            lat = re.search(r"""'lat':(.*?),""", rs).group(1)
            lng = re.search(r"""'lng':(.*?),""", rs).group(1)
            if n in url:
                yext_id.append(
                    {
                        "url": url,
                        "id": yext,
                        "name": name,
                        "type": loc_type,
                        "country": country,
                        "lng": lng,
                        "lat": lat,
                    }
                )

    yext_ids = {each["id"]: each for each in yext_id}

    def useAPI(link, yext_id):
        sessi = sgrequests.SgRequests().get(
            f"{link}cdn-cache.aspx?url=https%3A%2F%2Fcms.vizergy.com%2Fyext%2Findex.aspx%3FYextEntityId%3D{yext_id}%26Fields%3Daddress%2CmainPhone%2Chours%2Cmeta%26PageWidgetId%3D805821%26culturecode%3Den-US%26CacheMinutes%3D5%26callback%3DYextDataSingleLocation"
        )
        return json.loads(
            re.search(r"YextDataSingleLocation\((.*?)\);", sessi.text).group(1)
        )

    cleanYext = []

    for key in yext_ids:
        if yext_ids[key]["id"] == "":
            pass
        else:
            cleanYext.append(yext_ids[key])

    for k in cleanYext:
        y = k
        api = useAPI(y["url"], y["id"])["response"]["entities"][0]
        name = y["name"]
        street = api["address"]["line1"]
        city = api["address"]["city"]
        state = api["address"]["region"]
        if y["country"]:
            state = y["country"]
        if api["address"]["countryCode"] == "GB":
            state = "United Kingdom"
        zp = api["address"]["postalCode"]
        loc_type = y["type"]
        phone = api["mainPhone"]

        timeArray = []

        if "hours" in api:
            if api["hours"] is None:
                pass
            else:
                for ob in api["hours"]:
                    if ob == "holidayHours":
                        pass
                    else:
                        if api["hours"][ob] is None:
                            hours = missingString
                        else:
                            if api["hours"][ob]["openIntervals"] is None:
                                hours = missingString
                            else:
                                timeArray.append(
                                    "{} : {} - {}".format(
                                        ob.title(),
                                        api["hours"][ob]["openIntervals"][0][
                                            "startIn12HourFormat"
                                        ],
                                        api["hours"][ob]["openIntervals"][0][
                                            "endIn12HourFormat"
                                        ],
                                    )
                                )
                hours = ", ".join(timeArray)
        else:
            hours = missingString

        result.append(
            [
                locator_domain,
                y["url"],
                name,
                street,
                city,
                state,
                zp,
                api["address"]["countryCode"],
                api["meta"]["id"],
                phone,
                y["type"],
                y["lat"],
                y["lng"],
                hours,
            ]
        )

    r = []

    for el in result:
        el = [elem if elem else missingString for elem in el]
        r.append(el)

    return r


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
