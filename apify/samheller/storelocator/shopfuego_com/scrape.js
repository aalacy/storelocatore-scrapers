const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const requestPromise = require('request-promise');

Apify.main(async () => {
  const links = await pageList();
  const requestList = new Apify.RequestList({sources: links});
  await requestList.initialize();

  const crawler = new Apify.BasicCrawler({
    requestList,
    handleRequestFunction: async ({ request }) => {
      
      const html = await requestPromise(request.url);
      dom = new JSDOM(html);
      rows = dom.window.document.querySelectorAll('td > div > div.row');

      for (let row of rows){
        //retrieve lat/long from google maps link
        latlon = row.querySelector('a').getAttribute('href')
        .replace(/http.*@/, '') //Trim off front of URL
        .replace(/\/.*/, '') //Trim off end of URL
        .split(','); //split into array for easy reuse
        
        // Parse store info from text
        row = row.textContent
          .trim() // initial trim
          .replace(/\t/g, "")   // Remove excess spacing
          .replace(/\n\|/, '')  // Deal with edgecase where there's an errant newline
          .replace("|", "") // Remove decorative separator
          .replace("  ", " ") // Remove double spaces
          .split("\n") // Split on Newlines
          .filter((e) => {return e != ''}) // Filter out empty elements

        //Check for and handle edgecases
        if (isEdgeCase(row[0])){
          await handleEdgeCase(row, latlon);
          continue;
        }


        //Location name is first element
        locationName = row.shift();

        //Phone number is the last
        phone = row.pop().replace("Phone: ", "");

        //City/State/Zip now at the last
        area = row.pop().replace(",", "").split(" ");

        //Remaining information is the address, remove dupe spaces
        address = row.join(' ').replace("  ", " ");

        //split out city/state/zip data
        zip = area.pop();
        state = area.pop();
        city = area.join(" ");


        //Send it off
        await Apify.pushData([{
          locator_domain: 'shopfuego.com',
          location_name: locationName,
          street_address: address,
          city: city,
          state: state,
          zip: zip,
          country_code: 'US',
          store_number: "<MISSING>",
          phone: phone,
          location_type: "<MISSING>",
          latitude: latlon[0],
          longitude: latlon[1],
          hours_of_operation: "<MISSING>",
        }]);        
      }
      

		}
  })

  await crawler.run();
});

async function pageList(){
  return await axios({
    method: "GET",
    url: "https://www.shopfuego.com/Store-Locator-s/105.htm"
  }).then((resp) => {
    dom = new JSDOM(resp.data);
    links = [];
    for (let l of dom.window.document.querySelectorAll('td > a')){
      href = l.getAttribute('href');
      if (!href.startsWith('http')){href = "http://shopfuego.com" + href;}
      links.push({url: href})
    }
    return links;
  })
}

function isEdgeCase(location){
  switch (location.trim()){
    case 'Chandler Fashion Center' : return true; break;
    case 'Chandler Phoenix Premium Outlets': return true; break;
    default: return false; break;
  }
}

async function handleEdgeCase(row){
  if (row[0].trim() == 'Chandler Fashion Center'){
    fixed = {};
    fixed.locationName = row[0].trim()
    fixed.phone = row[3].replace('Phone: ', "");
    fixed.address = row[1] + " " + row[2].replace(/Chandler.*/, '');
    area = row[2].replace(/.*1042/, '').split(',');
    fixed.city = area.shift();
    fixed.state = area[0].split(" ")[1];
    fixed.zip = area[0].split(" ")[2];
  } 

  if (row[0].trim() == 'Chandler Phoenix Premium Outlets'){
    fixed = {};
    fixed.locationName = row[0].trim();
    fixed.phone = row[4].replace('Phone: ', "");
    fixed.address = row[1].trim() + " " + row[2].trim();
    area = row[3].split(',')
    fixed.city = area[0];
    area = area[1].trim().split(' ');
    fixed.state = area[0];
    fixed.zip = area[1];
  }
 
  await Apify.pushData([{
    locator_domain: 'shopfuego.com',
    location_name: fixed.locationName,
    street_address: fixed.address,
    city: fixed.city,
    state: fixed.state,
    zip: fixed.zip,
    country_code: 'US',
    store_number: "<MISSING>",
    phone: fixed.phone,
    location_type: "<MISSING>",
    latitude: latlon[0],
    longitude: latlon[1],
    hours_of_operation: "<MISSING>",
  }]);
}