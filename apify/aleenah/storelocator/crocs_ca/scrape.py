import csv
import sgzip
import requests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

all=[]
def fetch_data():
    # Your scraper here
    """search = sgzip.ClosestNSearch()
    # Initialize the search for the US and Canada
    search.initialize(country_codes=['ca'])

    # Fetch the first postal code to query
    postcode = search.next_zip()

    MAX_COUNT = 250
    MAX_DISTANCE = 100
    driver.get("https://www.crocs.ca/store-locator/stores,en_CA,pg.html")
    time.sleep(20)
    driver.switch_to.frame(driver.find_element_by_class_name('w-100'))
    #print(driver.page_source)
    #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'country6')))
    driver.find_element_by_id('searchradiusBtn').click()
    driver.find_element_by_id('radius100').click()
    driver.find_element_by_id('searchcountry').click()
    driver.find_element_by_id('country6').click() #canada
    while postcode:
        print(postcode)
        driver.find_element_by_id('inputaddress').send_keys(postcode)
        driver.find_element_by_id('search_button').click()
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'storeResults')))
        except:
            print("none")
            postcode = search.next_zip()
            driver.find_element_by_id('inputaddress').clear()
            continue
        results=driver.find_element_by_id('storeResults').find_elements_by_tag_name('li')
        driver.find_element_by_id('inputaddress').clear()
        for result in results:

        if len(results) >= MAX_COUNT:
        # Extract latitude/longitude coordinates for each store
            result_coords = parse_coords(results)
            search.max_count_update(result_coords)
        else:
            search.max_distance_update(MAX_DISTANCE)

        postcode = search.next_zip()"""
    search = sgzip.ClosestNSearch()
    # Initialize the search for the US and Canada
    search.initialize(country_codes=['ca'])
    count = 0
    # Fetch the first postal code to query
    postcode = search.next_zip()
    key_set=set([])
    MAX_DISTANCE_UPDATE=250
    while postcode:
        data='{"request":{"appkey":"1BC4F6AA-9BB9-11E6-953B-FA25F3F215A2","formdata":{"geoip":false,"dataview":"store_default","order":"icon DESC,_distance","limit":100000,"geolocs":{"geoloc":[{"addressline":"'+str(postcode)+'","country":"CA","latitude":"","longitude":""}]},"searchradius":"'+str(MAX_DISTANCE_UPDATE)+'","radiusuom":"km","where":{"TBLSTORESTATUS":{"in":"Open,OPEN,open"},"or":{"crocsretail":{"eq":"1"},"crocsoutlet":{"eq":"1"},"otherretailer":{"eq":"1"}}},"false":"0"}}}'

        res=requests.post("https://stores.crocs.com/rest/locatorsearch",data=data)

        #print(res)
        #print(postcode)
        #print(res.json())
        try:
            jso=res.json()["response"]["collection"]
        except:
            search.max_distance_update(MAX_DISTANCE_UPDATE)
            postcode = search.next_zip()
            continue

        for js in jso:

            if js["country"]!="CA":
                continue

            try:
                loc=js["name"]
            except:
                continue

            try:
                id=js["uid"]
            except:
                id = "<MISSING>"

            lat=js["latitude"]
            long=js["longitude"]
            street=js["address1"]
            state=js["province"]
            zip=js["postalcode"]
            if zip==None:
                zip="<MISSING>"
            city=js["city"]
            #print(city,zip,state)

            key=loc+city+zip+state

            if key in key_set:
                continue
            key_set.add(key)
            count += 1

            #print(js)
            try:
                tim=js["storehours"]
            except:
                tim=None

            if tim == "null" or tim=="" or tim ==None:
                tim="<MISSING>"
            else:
                tim="Mon: "+js["monopen"]+" - "+js["monclose"]+" Tue: "+js["tueopen"]+" - "+js["tueclose"]+" Wed: "+js["wedopen"]+" - "+js["wedclose"]+" Thu: "+js["thropen"]+" - "+js["thrclose"]+" Fri: "+js["friopen"]+" - "+js["friclose"]+" Sat: "+js["satopen"]+" - "+js["satclose"]+" Sun: "+js["sunopen"]+" - "+js["sunclose"]

            try:
                phone=js["phone"]
            except:
                phone=None

            if phone == "null" or phone=="" or phone ==None:
                phone="<MISSING>"

            type=js["tblstoretype"]

            all.append([
                "https://www.crocs.ca/",
                loc,
                street,
                city,
                state,
                zip,
                'CA',
                id,  # store #
                phone,  # phone
                type,  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                "https://stores.crocs.com/rest/locatorsearch"])

        search.max_distance_update(MAX_DISTANCE_UPDATE)
        postcode = search.next_zip()
    print(count)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

