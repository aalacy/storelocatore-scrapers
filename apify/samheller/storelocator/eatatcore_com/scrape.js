const Apify = require('apify');
const axios = require('axios');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const requestPromise = require('request-promise');

Apify.main(async () => {
  const links = await pageList();
  const requestList = new Apify.RequestList({sources: links});
  await requestList.initialize();
  /*
   * Exceptions Needing Handling: 
https://www.corelifeeatery.com/locations/latham-ny-2/
https://www.corelifeeatery.com/locations/maumee-oh-2/
   *
   */
  const crawler = new Apify.BasicCrawler({
    requestList,
    handleRequestFunction: async ({request}) => {
      const html = await requestPromise(request.url);
      document = new JSDOM(html).window.document;
      entry = document.querySelector('.column-content');
      store = request.url
        .split("/")
        .filter((e) => {return e !== ''})
        .pop()
      latlon = latLonFromLink(entry.querySelector('a').getAttribute('href'));
      address = entry.querySelector('p:nth-child(2)').textContent.split("\n");
      if (address.length == 5){
        address = [address[0], address[2], address[3], address[4]]
      }
      area = parseArea(address[1]);
      hours = entry.querySelector('p:nth-child(5)').textContent;

      // Apify.pushData([{
      console.log([{
        locator_domain: 'corelifeeatery.com',
        location_name: store,
        street_address: address[0],
        city: area.city,
        state: area.state,
        zip: area.zip,
        country_code: 'US',
        store_number: '<MISSING>',
        phone: address.pop().replace('Phone:', '').trim(),
        location_type: '<MISSING>',
        latitude: latlon.lat,
        longitude: latlon.lon,
        hours_of_operation: hours,
      }])
    }
  })
  await crawler.run()
});



async function pageList(){
  return await axios({
    method: "GET",
    url: "https://www.corelifeeatery.com/locations/"
  }).then((resp) => {
    document = new JSDOM(resp.data).window.document;    
    links = [];
    for (let d of document.querySelectorAll('.grid-item')){
      links.push({url: d.querySelector('a').getAttribute('href')});
    }
    return links;
  });
}

function parseArea(area){
  parsed = {city: '', state: '', zip: ''};
  area = area.split(',');
  parsed.city = area[0];
  area = area[1].split(' ');
  parsed.zip = area.pop();
  parsed.state = area.join(' ').trim();
  return parsed;
}

function latLonFromLink(href){
  [lat, lon] = href
    .replace(/^.*\@/, '') //strip everything up to latlong string
    .replace(/\/.*/, '') // strip everything after latlong string
    .split(','); //split on comma

  //Handle link extraction failures
  if (lat == 'https' || lon == undefined){return {lat: '<MISSING>', lon: '<MISSING>'}}
  return {lat: lat, lon: lon}
}

function sanitize(textRow){
  sane = [];
  for (s of textRow.split("\n")){
    s = s.trim();
    if (s !== ''){sane.push(s);}
  }
  return sane;
}