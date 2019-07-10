const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const parser = require('parse-address');

Apify.main(async () => {
  const links = await pageList();
  const requestList = new Apify.RequestList({sources: links});
  await requestList.initialize();
  
  const crawler = new Apify.CheerioCrawler({
    requestList,
    minConcurrrency: 10,
    handlePageTimeoutSecs: 30,
    handlePageFunction: async ({request, html, $}) => {
      try {
        location = parseStoreLocationDetails($('.location-details').text());
        amenities = parseStoreAmenitiesDetails($('.location-features').html());
        storeId = request.url.replace(/([A-Z]|[a-z]|-|\/|:|\.)*/g, '');
        await Apify.pushData([{
          locator_domain: 'altaconvenience.com',
          location_name: `Store ${storeId}`,
          street_address: `${location.address.number} ${location.address.prefix} ${location.address.street} ${location.address.type}`.replace('undefined', ''),
          city: location.address.city == undefined ? '<MISSING>' : location.address.city,
          state: location.address.state == undefined ? '<MISSING>' : location.address.state,
          zip: location.address.zip == undefined ? '<MISSING>' : location.address.zip,
          country_code: 'US',
          store_number: storeId,
          phone: location.phone.length < 10 ? '<MISSING>' : location.phone,
          location_type: amenities,
          latitude: '<MISSING>',
          longitude: '<MISSING>',
          hours_of_operation: location.hours.join(", ")
        }]);
      } catch (e){
        //As of writing there are 3 edge cases where the store details page doesn't load.
        //Use the summary data on the location listing page to create an entry instead
        backupData = request.userData.text.split("\n");
        storeId = backupData[0].replace(/Alta.*Store /, '').trim();
        address = backupData[1].trim();
        //This is really ugly, but given the small number of edge cases I'm okay with it for now
        city = backupData[2].trim().split(" ")[0].replace(',', '');
        state = backupData[2].trim().split(" ")[1].replace('.', '');
        zip = backupData[2].trim().split(" ")[2]
        phone = backupData[3].trim();

        await Apify.pushData([{
          locator_domain: 'altaconvenience.com',
          location_name: `Store ${storeId}`,
          street_address: address,
          city: city,
          state: state,
          zip: zip,
          country_code: 'US',
          store_number: storeId,
          phone: phone,
          location_type: '<MISSING>',
          latitude: '<MISSING>',
          longitude: '<MISSING>',
          hours_of_operation: '<MISSING>'
        }]);
      }
    }
  });

  await crawler.run();
});



function parseStoreAmenitiesDetails(featuresHtml){
  amenitiesDom = new JSDOM(featuresHtml);
  amenities = amenitiesDom.window.document.querySelector('div > p').textContent;
  sorted = [];
  for (let a of amenities.split("\n")){
    a = a.trim();
    if (a !== ''){sorted.push(a)}
  }
  sorted.sort();
  return sorted.join(',').replace('ATMBeer', 'ATM,Beer')
}

function parseStoreLocationDetails(detailsText){
  ret = {address: [], hours: [], phone: ""}
  loc = detailsText.split('\n') //Pull the text value from the location details and split on newlines
  .filter((el) => {return el.trim() != ""}); //Apply filter to remove any empty array entries

  //Sort out all the entries
  for (let entry of loc){
    entry = entry.trim().replace(':', '');
    if (entry.startsWith('Location Details')){}
    else if (entry.startsWith("Phone")){ret.phone = entry.replace("Phone", "").trim();}
    else if (entry.startsWith("Hours")){ret.hours.push(entry.replace('Hours', '').trim());}
    else if (entry.startsWith("Open")){ret.hours.push(entry);}
    else {ret.address.push(entry);}
  }

  //Use address parser library to extract consistently usable addresses
  ret.address = parser.parseLocation(ret.address.join(" "));
  if (ret.address.prefix == undefined){ret.address.prefix = ""}
  return ret;
}


async function pageList() {
  return await axios({
    method: "GET",
    url: "http://altaconvenience.com/Find-a-Store"
  }).then((resp) => {
    dom = new JSDOM(resp.data);
    links = [];
    for (let l of dom.window.document.querySelectorAll("div.location")){
      links.push({
        url: "http://altaconvenience.com" + l.querySelector('a').getAttribute('href'), 
        userData: {text: l.textContent}})
    }
    return links;
  })
  
}
