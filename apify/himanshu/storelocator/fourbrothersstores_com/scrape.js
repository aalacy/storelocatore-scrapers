const Apify = require('apify');
// const cheerio=require('cheerio');
(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'http://fourbrothersstores.com/index.cfm/store-locator/' }],
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

			// Begin scraper
      var items=[];
      var main=$('#storelocator').children().find('#store_listing');
      main.children().each(function(index){
        main.find('.col_'+(index+1)).find('h3').each(function(index1){
            var temp_add=main.find('.col_'+(index+1)).children('ul').eq(index1).children('li').children("ul");
            temp_add.each(function(index3){
                var mainaddress=temp_add.eq(index3).find('li.txt_address').html().split('<br>'); 
                address=mainaddress[0];
                var ct=mainaddress[1].replace(/\n\t\t+/g, '').split(', ')
                if(ct.length==1)
                      ct=mainaddress[1].replace(/\n\t\t+/g, '').split(' ');
                
                var city=ct[0];
                
                var state="";
                var zip="";
                if(ct.length==3){
                    state=ct[1];
                    zip=ct[2];
                }
                else{
                  state=ct[1].split(' ')[0];
                  zip=ct[1].split(' ')[1];
                }
                var phone=temp_add.eq(index3).find('li.txt_manager').text().split('Phone: ')[1]; 
                var hour=temp_add.eq(index3).find('li.txt_hours').text().split('Hours: ')[1]; 
                var direction=temp_add.eq(index3).find('li.txt_directions').find('a').attr('href'); 
                items.push({
                      locator_domain: 'http://fourbrothersstores.com',
                      location_name: main.find('.col_'+(index+1)).children('h3').eq(index1).text(),
                      street_address: address,
                      city: city,
                      state: state,
                      zip: parseFloat(zip),
                      country_code: 'US',
                      store_number: '<MISSING>',
                      phone: phone?phone:'<MISSING>'  ,
                      location_type: 'fourbrothers',
                      latitude: '<MISSING>',
                      longitude: '<MISSING>',
                      hours_of_operation: hour});
            });
          });
      });
      // console.log(items);
      
			await Apify.pushData(items);
      // setInterval(()=> {
      //   console.log("11");
        
      // },1000)
			// End scraper

    },
  });

  await crawler.run();
})();
