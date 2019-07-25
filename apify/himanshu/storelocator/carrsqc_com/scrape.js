const request=require('request');
const Apify = require('apify');

const cheerio=require('cheerio');

var url_temp = 'https://local.carrsqc.com/ak.html';

var url = 'https://local.carrsqc.com/';
 
async function scrape(){

return new Promise(async (resolve,reject)=>{
request(url_temp,  function(err,res,html){

   if(!err && res.statusCode==200){
      
    const $  =cheerio.load(html);
    var main = $('#main').find('.Main-content').find('.c-directory-list-content').find('.c-directory-list-content-item') ;
    var items=[];


  function mainhead(i)

        {
          if(main.length>i)

            {
          const link = url+ main.eq(i).find('a').attr('href');
       
         if(link.match(/\d+/g)==null){
                                          request(link,function(err,res,html){  
                                            
                                            const $  =cheerio.load(html);
                                              if(!err && res.statusCode==200){
                                                var main1 = $('.Main-content').find('.LocationList-teasers').find('.Teaser-links') ;

                                               
                                                function mainhead1(i1){

                                                  if(main1.length>i1){
                                  
                                                  const link2_temp = $('.Main-content').find('.LocationList-teasers').find('.Teaser-links').eq(i1);
                                                  const link2_temp1= url+link2_temp.find('a').eq(1).attr('href');
                                                  const link2 = link2_temp1.replace('../','');
                                                 // console.log(link2);
                                            
                                                     request(link2,function(err,res,html){    
                                                          if(!err && res.statusCode==200){
                                                            const $ =cheerio.load(html);

                                                            var main2 = $('.Main-content').find('#address').children();
                                                            //console.log(main2.length);

                                                            function mainhead2(i2){

                                                              if(1>i2)
                                        
                                                              {

                                                          var address = $('#address').find('.c-address-street-1').text();
                                                          
                                                          var location_name = $('#location-name').find('.LocationName-geo').text();
                                                          var city = $('#address').find('.c-address-city').text();
                                                          var state = $('#address').find('.c-address-state').text();
                                                          var phone = $('.LocationInfo-phones').find('.c-phone-number-link').text();
                                                          var zip = $('#address').find('.c-address-postal-code').text() ;
                                                          var Storehour = $('.c-location-hours-details-row').text();
                                                          var latitude_temp =  $('script#js-map-config-dir-map-desktop[type="text/data"]').html();
                                                          var latitude_temp1 =  JSON.parse(latitude_temp);
                                                          
                                                          var latitude = latitude_temp1.locs[0].latitude;
                                                          var longitude = latitude_temp1.locs[0].longitude;
                                                        
                                      
                                                          items.push({ 
                                      
                                                          locator_domain: url, 
                                                           location_name:location_name,
                                                          street_address: address,
                                                          city: city,
                                                          state: state,
                                                          zip: zip,
                                                          country_code: 'US',
                                                          store_number: '<MISSING>',
                                                          phone: phone, 
                                                          location_type: 'carrsqc',
                                                          latitude: latitude.toString(), 
                                                          longitude: longitude.toString(), 
                                                          hours_of_operation: Storehour
                                                        
                                                        });
                                                     
                                      
                                                        mainhead2(i2+1);

                                                        }

                                                    else{

                                                    mainhead1(i1+1);

                                                    }

                                                  }

                                            mainhead2(0);
                                                          }
                                                          // console.log(items);
                                                      });
  
                
                                                        }

                               else{

                                mainhead(i+1);
                                   }
     
                          }
                             
                      mainhead1(0);

                 }

            });
          }
                                  else{
                                                              
                                    request(link,function(err,res,html){    
                                      if(!err && res.statusCode==200){
                                        const $ =cheerio.load(html);

                                        var main2 = $('.Main-content').find('#address').children();
                                        //console.log(main2.length);

                                        function mainhead3(i2){

                                          if(1>i2)

                                          {

                                      var address = $('#address').find('.c-address-street-1').text();
                                      
                                      var location_name = $('#location-name').find('.LocationName-geo').text();
                                      var city = $('#address').find('.c-address-city').text();
                                      var state = $('#address').find('.c-address-state').text();
                                      var phone = $('.LocationInfo-phones').find('.c-phone-number-link').text();
                                      var zip = $('#address').find('.c-address-postal-code').text() ;
                                      var Storehour = $('.c-location-hours-details-row').text();
                                      var latitude_temp =  $('script#js-map-config-dir-map-desktop[type="text/data"]').html();
                                      var latitude_temp1 =  JSON.parse(latitude_temp);
                                      
                                      var latitude = latitude_temp1.locs[0].latitude;
                                      var longitude = latitude_temp1.locs[0].longitude;
                                      
                                      items.push({ 

                                      locator_domain: url, 
                                      location_name:location_name,
                                      street_address: address,
                                      city: city,
                                      state: state,
                                      zip: zip,
                                      country_code: 'US',
                                      store_number: '<MISSING>',
                                      phone: phone, 
                                      location_type: 'carrsqc',
                                      latitude: latitude.toString(), 
                                      longitude: longitude.toString(), 
                                      hours_of_operation: Storehour
                                    
                                    });
                                    
                                  mainhead3(i2+1);

                                    }

                                else{

                                mainhead(i+1);

                                }

                              }

                        mainhead3(0);
                                      }
                                      
                                  });
          }

          }

          else{
              resolve(items);
              }
      }

   mainhead(0);

   }
}); 

});

}


Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});