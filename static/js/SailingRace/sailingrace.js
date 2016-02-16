var windMarkers = [];
var windIcon;

function showWindOnMap()
{
    var NWBound = map.getBounds().getNorthWest();
    var SEBound = map.getBounds().getSouthEast();
    
    
    windIcon = L.icon({  
        iconUrl: '/static/images/windicon.png',
        iconSize:     [50, 50],
        iconAnchor:   [25, 25],
    });
    
    console.log("Drawing wind");
    
    for(var x = NWBound.lon.toFixed(0); x < SEBound.lat.toFixed(0); x++)
    {
        for(var y = NWBound.lat.toFixed(0); y < SEBound.lat.toFixed(0); y++)
        {          
            $.ajax({
                url: 'http://api.openweathermap.org/data/2.5/weather?lat=' + y + '&lon=' + x +'&appid=89c15fa0109218f9c81b1567fd5958cc',
                type: 'get',
                success: function(data) {
                             var windSpeed = data['wind']['speed']*1.94384; //1,94384 is to convert to knots
                             var windDirection = data['wind']['deg'];
                             
                             if(typeof windMarkers[x] == 'undefined')
                                windMarkers[x] = [];
                                
                             windMarkers[x][y] = L.marker([y, x], {
                                    icon: windIcon
                             }).addTo(map).setRotationOrigin([25,25]).setRotationAngle(windDirection);
                                                
                        }
            });
        }
    }
}