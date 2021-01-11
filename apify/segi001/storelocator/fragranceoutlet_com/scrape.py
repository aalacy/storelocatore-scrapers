import csv
import sgrequests
import bs4
import itertools
import re


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    locator_domain = "https://www.fragranceoutlet.com/"
    sitemap = "https://www.fragranceoutlet.com/sitemap_pages_1.xml"
    missingString = "<MISSING>"

    sess = sgrequests.SgRequests()

    soup = bs4.BeautifulSoup(sess.get(sitemap).text, features="lxml")

    result = []
    el = []

    def getLocJSON(es):
        if len(es) == 4:
            if es[2] in es[1]:
                es.pop(2)
            elif "Suite" in es[1]:
                es[0] = es[0] + es[1].replace(es[2], "")
                es.pop(1)
        if es[1] == "6Las Vegas, NV 89123":
            es[1] = es[1][1:]
        elif es[1] == "212San Marcos, TX 78666":
            es[1] = es[1].replace("212", "")
            es[0] = es[0] + " 212"
        elif es[1] == "Suite: 241Bethlehem, PA 18015":
            es[1] = es[1].replace("Suite: 241", "")
            es[0] = es[0] + " Suite: 241"

        zipc = "".join(filter(str.isdigit, es[1]))
        city = es[1].replace(zipc, "").split(",")[0]
        state = es[1].replace(zipc, "").split(",")[1]

        addressJSON = {
            "state": state,
            "city": city,
            "zip": zipc,
            "address": es[0],
            "phone": es[-1],
        }

        return addressJSON

    for loc in soup.findAll("loc"):
        slug = "fragrance-outlet"
        if slug in loc.text:
            url = loc.text
            ignore = "blog"
            if ignore in url:
                pass
            else:
                urlsoup = bs4.BeautifulSoup(sess.get(url).text, features="lxml")
                name = (
                    urlsoup.find("header", {"class": "page-header"})
                    .text.title()
                    .strip()
                )
                lat = ""
                lng = ""
                a = urlsoup.findAll("td")
                es = []
                for ass in a:
                    p = ass.findAll("p")
                    for ps in p:
                        if ps.text == "Fragrance Outlet":
                            ps_a = ps.find("a")
                            if not ps_a.has_attr("href"):
                                lat = missingString
                                lng = missingString
                            else:
                                if "https://www.google.com/maps?ll=" in ps_a["href"]:
                                    latlng = (
                                        re.search(r"ll=(.*?)&", str(ps_a["href"]))
                                        .group(0)
                                        .split(",")
                                    )
                                    if len(latlng) == 2:
                                        lat = latlng[0].replace("@", "")
                                        lng = latlng[1]
                                    else:
                                        lat = missingString
                                        lng = missingString
                                elif (
                                    "https://www.google.com/maps/dir//" in ps_a["href"]
                                ):
                                    latlng = (
                                        ps_a["href"]
                                        .replace(
                                            "https://www.google.com/maps/dir//", ""
                                        )
                                        .replace("https://www.google.com/maps/dir/", "")
                                        .split("/")[0]
                                        .split(",")
                                    )
                                    if len(latlng) == 2:
                                        lat = latlng[0]
                                        lng = latlng[1]
                                    else:
                                        lat = missingString
                                        lng = missingString
                                elif (
                                    "https://www.google.com/maps/place" in ps_a["href"]
                                ):
                                    latlng = re.search(
                                        r"@(.*?)/", str(ps_a["href"])
                                    ).group(0)
                                    if len(latlng) == 2:
                                        lat = latlng[0].replace("@", "")
                                        lng = latlng[1]
                                    else:
                                        lat = missingString
                                        lng = missingString
                                elif "https://www.google.com/maps/" in ps_a["href"]:
                                    latlng = (
                                        ps_a["href"]
                                        .replace("https://www.google.com/maps/@", "")
                                        .split(",")
                                    )
                                    if len(latlng) == 2:
                                        lat = latlng[0]
                                        lng = latlng[1]
                                    else:
                                        lat = missingString
                                        lng = missingString
                                elif "goo.gl" in ps_a["href"]:
                                    lat = missingString
                                    lng = missingString
                        elif "Email:" in ps.text:
                            pass
                        else:
                            e = (
                                ps.get_text(separator="%")
                                .replace("Phone:", "")
                                .split("%")
                            )
                            if len(e) == 4:
                                if " " in e:
                                    e.pop(2)
                                if e[2] in e[1]:
                                    e[0] = "{} {}".format(e[0], e[1])
                                es = [
                                    ele.replace(u"\xa0", u"").replace(u"\ufeff", u"")
                                    for ele in e
                                ]
                            elif len(e) == 5:
                                e[0] = "{} {}".format(e[0], e[1])
                                e.pop(1)
                                if " " in e:
                                    e.remove(" ")
                                es = [
                                    ele.replace(u"\xa0", u"").replace(u"\ufeff", u"")
                                    for ele in e
                                ]
                            elif len(e) == 6:
                                if "20.4151" in e:
                                    e[-1] = "{}{}".format(e[-2], e[-1])
                                    e[0] = "{} {}".format(e[0], e[1])
                                    e.pop(1)
                                    e.pop(-2)
                                    e.remove(" ")
                                    es = [
                                        ele.replace(u"\xa0", u"").replace(
                                            u"\ufeff", u""
                                        )
                                        for ele in e
                                    ]
                                else:
                                    e[0] = "{} {}".format(e[0], e[1])
                                    e[2] = "{}{}".format(e[2], e[3])
                                    e.pop(1)
                                    e.pop(3)
                                    if " " in e:
                                        e.remove(" ")
                                    es = [
                                        ele.replace(u"\xa0", u"").replace(
                                            u"\ufeff", u""
                                        )
                                        for ele in e
                                    ]
                            elif len(e) == 7:
                                e[0] = "{} {} {}".format(e[0], e[1], e[2])
                                e.pop(1)
                                if e[1] in e[0]:
                                    e.pop(1)
                                if " " in e:
                                    e.remove(" ")
                                e[-1] = "{}{}".format(e[-2], e[-1])
                                e.pop(-2)
                                es = [
                                    ele.replace(u"\xa0", u"").replace(u"\ufeff", u"")
                                    for ele in e
                                ]

                JSON = getLocJSON(es)

                hours = urlsoup.findAll("div", {"class": "opening-time"})

                time = []

                for t in hours:
                    time.append(t.text.strip().split("\n"))

                hours_of_operation = " ".join(itertools.chain.from_iterable(time))

                cc = urlsoup.find("script", {"id": "apple-pay-shop-capabilities"})

                countryCode = (
                    re.search(r'"countryCode":(.*?),', str(cc))
                    .group(1)
                    .replace('"', "")
                )

                result.append(
                    [
                        locator_domain,
                        url,
                        name,
                        JSON["address"],
                        JSON["city"],
                        JSON["state"],
                        JSON["zip"],
                        countryCode,
                        missingString,
                        JSON["phone"],
                        missingString,
                        lat,
                        lng,
                        hours_of_operation,
                    ]
                )
        else:
            pass

    for r in result:
        for el in r:
            el.replace(u"\ufeff", u"")

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
