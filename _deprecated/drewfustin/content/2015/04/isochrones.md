Title: Isochrones using the Google Maps Distance Matrix API
Date: 2015-04-29
Slug: isochrones
URL: isochrones
Image: http://drewfustin.com/images/isochrones/og.png

[tl;dr] I wrote a Python module called [isocronut](https://github.com/drewfustin/isocronut) that will calculate isochrones around an origin point.

---

I live in a neighborhood in Chicago that is close to pretty much everything, as is the case with many affluent neighborhoods in big cities (and, sadly, [not the case in the poorer neighborhoods...](http://www.marigallagher.com/site_media/dynamic/project_files/LaSalle_Bank_Chicago_Food_Desert_4_Page_Brochure.pdf)). But, in the case of the [West Loop](http://www.wsj.com/articles/hot-in-chicago-the-west-loop-neighborhood-1412869988), this is particularly true. For instance, I'm within walking distance of the restaurants of 2 of the 5 "Best Chef: Great Lakes" nominees for this year's [James Beard Awards](http://www.jamesbeard.org/blog/complete-2015-jbf-award-nominees) (last year, it was 3 of the 5). Fittingly enough, I'm also within walking distance _of_ this year's James Beard Awards -- they're being held at the Lyric Opera in a couple weeks, which is along my walk to work.

When my wife and I were deciding on where to buy in Chicago, a huge factor -- along with quality of the neighborhood public school -- was the walkability of the area and the proximity to the trains (for her commute) and the Loop (for mine). And, when thinking about how long it takes to travel a certain distance, either on foot or in the car, it makes sense to consider something called an isochrone. An [isochrone](http://en.wikipedia.org/wiki/Isochrone_map) is a contour that can be drawn around an origin point (e.g. our condo) that connects points of equal travel time. So, for instance, I can walk to any point along the border of the contour below in 15 minutes (and any place within that contour in less than 15 minutes). And, no that is not my actual address -- but it _is_ the address of a [Harold's Chicken Shack](http://www.haroldswestloop.com/), which is quite wonderful.

<center>
<iframe
  width="600"
  height="450"
  frameborder="0" style="border:0"
  src="/html/isochrones/harolds_15m_walking_isochrone.html">
</iframe>
</center>

### Google Maps API Access

In order to generate isochrones such as these, I made use of the [Google Maps API](https://developers.google.com/maps/). If you've never used the Google Maps API before, well then, buddy, now's your chance. It's not overly difficult, but it does have some tricky moments. If you're familiar with this API (or even APIs, in general), you can probably figure out the next several paragraphs yourself. I'll save your eyes from glazing over -- skip ahead to whichever section seems least boring to you.

If you have a Google Maps API for Work, you're in luck! On one hand, you have much softer usage limits in place. In addition, you get to make use of Google's traffic information, which is extremely useful in making accurate driving isochrones that line up to reality (or any time other than the middle of the night when there's no traffic). But beware that it just requires extra security work from you up front. Make note of your Client ID and Crypto Key and, for goodness sake, _get permission from the proper authorities at work before using their API key_.

If you don't have access to a Work API, the first thing you need to do is get yourself a [Google Develop project](https://console.developers.google.com/project). Click "Create Project" and name it something catchy like "Isochrones." Once created, you can click your project name, and you will be taken to a screen with a list on the left containing "APIs & auth" with subheadings containing "APIs" and "Credentials." Go to "APIs" and click "more" under "Google Maps APIs." For this project, we'll make use of both the "Geocoding API" and the "Distance Matrix API," so click on each of those and click "Enable API." Finally, go to the "Credentials" subheading on the left, click "Create new Key" under "Public API access," and click "Browser key" then "Create."

After all that clicking, your API project is now set up with Google. They'll use your API key that is now listed to track all your API usage, to make sure you aren't going over your limits. There are limits (the Distance Matrix API allows only 100 elements per 10 seconds and 2,500 elements per day if you have a free API). Sometimes this requires you to take some time off. Sometimes it requires you to slow your code down. Be aware.

With the Python module I wrote, I access these credentials from an external file. If you're so inclined to do the same instead of hard-coding them in, open up your editor of choice and create a file called 'google_maps.cfg' that will contain your API key (or Client ID and Crypto Key, if you are using API for Work). In a folder you have noted and can point the script to, make a file that looks just like this (leaving some fields blank, depending on if you are using the Free or Work API), except that it actually has your credentials in it:

```
[api]
api_number=<YOUR API KEY>
client_id=<YOUR CLIENT ID>
crypto_key=<YOUR CRYPTO KEY>
```

### Using the Google Maps API

As mentioned, we'll use the Geocoding API and the Distance Matrix API. The Geocoding API is slightly more straight forward, so let's start there. This entire project is [hosted on my github account](https://github.com/drewfustin/isocronut), so I'm just going to post relevant snippets to explain the code that is detailed there (with good comments!). Hopefully it's clear enough here.

#### Geocoding API

The Geocoding API is used in transforming a street address string into its corresponding [lat, lng] pair. In general, API use is as simple as creating a URL to pass and then reading the JSON (or XML, if that's your choice) that is returned. In this case, take your address string (let's use the Harold's again) and replace any space with a +, like so: 'address=804+W+Washington+Chicago'. If you're using the free API, append to this string '&key=<YOUR API KEY HERE\>'. Place that at the end of the prefix 'https://maps.googleapis.com/maps/api/geocode/json?' and [baby, you've got a stew going](https://www.youtube.com/watch?v=Sr2PlqXw03Y).

In Python, with address_str as '804+W+Washington+Chicago' and key as 'ThisI$_Yr_ap_iKEy' (but, you know, actually your API key) this looks like:

```python
prefix = 'https://maps.googleapis.com/maps/api/geocode/json'
url = urlparse.urlparse('{0}?address={1}&key={2}'.format(prefix,
                                                         address_str,
                                                         key))
full_url = url.scheme + '://' + url.netloc + url.path + '?' + url.query
```

With a Work API account, this is [entirely more complicated](https://developers.google.com/maps/documentation/business/webservices/auth). Security requires you generate a signature each time you send a request, and this is done with Base64 encoding and HMAC-SHA1 algorithm and other such nonsense that I don't remember anymore. But, the code below probably still works (with address_str the same, and client='YOUR CLIENT ID' and private_key='YOUR CRYPTO KEY'):

```python
prefix = 'https://maps.googleapis.com/maps/api/geocode/json'
url = urlparse.urlparse('{0}?address={1}&client={2}'.format(prefix,
                                                            address_str,
                                                            client))
url_to_sign = url.path + "?" + url.query
decoded_key = base64.urlsafe_b64decode(private_key)
signature = hmac.new(decoded_key, url_to_sign, hashlib.sha1)
encoded_signature = base64.urlsafe_b64encode(signature.digest())
original_url = url.scheme + '://' + url.netloc + url.path + '?' + url.query
full_url = original_url + '&signature=' + encoded_signature
```

With full_url in hand, send this as a request, interpret the JSON, and you've got your geocode [lat, lng] Python 2-list!

```python
req = urllib2.Request(full_url)
opener = urllib2.build_opener()
f = opener.open(req)
d = simplejson.load(f)
geocode = [d['results'][0]['geometry']['location']['lat'],
           d['results'][0]['geometry']['location']['lng']]
```

#### Distance Matrix API

The Distance Matrix API is more complicated only in that it has more parameters that you can pass to it and a much more complicated JSON return. But, it provides the meat for the isochrone algorithm. The Distance Matrix API returns a matrix of travel times and distances given a list of origins and destinations, with each element of the matrix corresponding to one origin-destination pair. To calculate isochrones, we'll be using only one origin (so this is more of a Distance Vector, I guess), and the destination points will be an set of points arranged symmetrically at different angles around the origin (each a radius $r_i$ away from the origin that varies as we traverse through the algorithm).

In general, the Distance Matrix API takes origins and destinations as either address strings (as written before), with groups concatenated with a | symbol (e.g. 'origins=Address+1|Address+2&destinations=41.88,-87.62|Address+3'). In our case, we have only one origin and a set of destinations that are chosen for us in the algorithm later. So, I won't bother with constructing those strings explicitly here. You can also pass it [several optional parameters](https://developers.google.com/maps/documentation/distancematrix/#RequestParameters), which I have hard-coded in (but you can change, if you're so inclined -- I made 'mode=walking' for the sample at the start, for example). Otherwise, all the steps above for building a proper URL to pass are the same.

The JSON output is in the form of a matrix, with 'rows' corresponding to origins and 'elements' corresponding to destinations. To parse our JSON, we'll have just one row and multiple elements. Our 'parse_json' function will then take a URL as input, send it as a request, read the JSON return, and return a list of lists of the form [addresses, durations], with durations being in minutes:

```python
def parse_json(url=''):
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    d = simplejson.load(f)
    i = 0
    durations = [0] * len(addresses)
    for row in d['rows'][0]['elements']:
        if 'duration_in_traffic' in row:
            durations[i] = row['duration_in_traffic']['value'] / 60
        else:
            durations[i] = row['duration']['value'] / 60
        i += 1
    return [addresses, durations]
```

### Selecting Destinations and the Evils of Spherical Geometry

Given an origin address (which is translated into a [lat, lng] pair by the geocode address function), we need to select a series of destination addresses which will be chosen by finding $n$ points distributed symmetrically (in angle) around the origin point. For each destination point around the origin (which is defined by a radius $r_i$ and bearing $b_i$), we need to calculate the corresponding [lat$_i$, lng$_i$]. This isn't as simple as using the Pythagorean theorem in Cartesian space because we're on a sphere (consider that the distance in miles between two points of longitude in Florida is considerably different than it is in Canada). We have to use these complicated Haversine things. Using $R = $ 3,963 miles (the radius of the Earth) and converting the origin [lat, lng] and the bearing $b_i$ into radians, the latitude of the destination is:

$$ \mathrm{lat}_i = \mathrm{asin}\left[\sin(\mathrm{lat}) \cos(r_i / R) + \cos(\mathrm{lat}) \sin(r_i / R) \cos(b_i)\right] $$

and the longitude is:

$$ \mathrm{lng}_i = \mathrm{lng} + \mathrm{atan2}\left[\sin(b_i) \sin(r_i / R) \cos(\mathrm{lat}), \cos(r_i / R) - \sin(\mathrm{lat}) \sin(\mathrm{lat}_i)\right] $$

In python, this looks like (with 'r' playing the role of the radius of Earth, and 'radius' and 'bearing' corresponding to the destination):

```python
from math import cos, sin, tan, sqrt, pi, radians, degrees, asin, atan2

r = 3963.1676
bearing = radians(angle)
lat1 = radians(origin_geocode[0])
lng1 = radians(origin_geocode[1])
lat2 = asin(sin(lat1) * cos(radius / r) + cos(lat1) * sin(radius / r) * cos(bearing))
lng2 = lng1 + atan2(sin(bearing) * sin(radius / r) * cos(lat1), cos(radius / r) - sin(lat1) * sin(lat2))
lat2 = degrees(lat2)
lng2 = degrees(lng2)
```

### Finally, Calculating Isochrones

At long last, we've built up the machinery to continue. We have an origin address which we've geocoded into [lat, lng]. We have a number $n$ of bearing angles $b_i$ that we can calculate the destination [lat<sub>_i_</sub>, lng<sub>_i_</sub>] pairs for, given a particular $r_i$. The crux of our isochrone builder is then to perform something like a binary search in radius along each bearing angle. The beauty of the Distance Matrix API is that it allows us to perform one search along _each_ bearing angle with only one API call (as long as we stay within output size limits, e.g. 100 elements per query). This greatly reduces our API request load and allows us to stay within budget.

The algorithm is as follows:

1. Start with an initial radius guess 'rad1' which is a list of length $n$, each element being something like 'duration' / 12 (where 'duration' corresponds to the minute-size of the isochrone).
2. For each angle symmetrically distributed around the origin (stored in list 'phi1'), calculate the destination [lat$_i$, lng$_i$] pair using the method described above. Store these in a list of 2-lists called 'iso' -- this will be your final output isochrone, eventually. It will look something like [[lat$_0$, lng$_0$], [lat$_1$, lng$_1$], ...].
3. Create a URL using the origin address or geocode and destination [lat$_i$, lng$_i$] pairs stored in 'iso' and pass this to the Distance Matrix API. Parse the JSON and return the durations to each point.
4. For each point $i$, if the API-returned duration is greater than the desired isochrone 'duration' (in actuality, beyond 'duration' plus some 'tolerance' -- the returned duration should never really exactly equal what we want), set the $i$th component of 'rad1' to the mean of what it just was and the smallest its ever been in the search (or 0 if it's never been smaller than it is now). If the API-returned duration is less than the desired isochrone 'duration' (minus some 'tolerance'), set the $i$th component of 'rad1' to the mean of what it just was and the largest its ever been in the search (or something big but not too big).
5. If the API-returned duration for the $i$th component is within some 'tolerance' of the isochrone 'duration', just leave it alone this time.
6. Continue this until no components of 'rad1' change or we have churned too long (in practice, _always_ make sure your while loops don't go on into infinity!).

When this is done, you have your isochrone! In code, this looks like:

```python
# Make a radius list, one element for each angle,
#   whose elements will update until the isochrone is found
rad1 = [duration / 12] * number_of_angles  # initial r guess based on 5 mph speed
phi1 = [i * (360 / number_of_angles) for i in range(number_of_angles)]
data0 = [0] * number_of_angles
rad0 = [0] * number_of_angles
rmin = [0] * number_of_angles
rmax = [1.25 * duration] * number_of_angles  # rmax based on 75 mph speed
iso = [[0, 0]] * number_of_angles

# Counter to ensure we're not getting out of hand
j = 0

# Here's where the binary search starts
while sum([a - b for a, b in zip(rad0, rad1)]) != 0:
    rad2 = [0] * number_of_angles
    for i in range(number_of_angles):
        iso[i] = select_destination(origin, phi1[i], rad1[i], access_type, config_path)
        time.sleep(0.1)
    url = build_url(origin, iso, access_type, config_path)
    data = parse_json(url)
    for i in range(number_of_angles):
        if (data[1][i] < (duration - tolerance)) & (data0[i] != data[0][i]):
            rad2[i] = (rmax[i] + rad1[i]) / 2
            rmin[i] = rad1[i]
        elif (data[1][i] > (duration + tolerance)) & (data0[i] != data[0][i]):
            rad2[i] = (rmin[i] + rad1[i]) / 2
            rmax[i] = rad1[i]
        else:
            rad2[i] = rad1[i]
        data0[i] = data[0][i]
    rad0 = rad1
    rad1 = rad2
    j += 1
    if j > 30:
        raise Exception("This is taking too long, so I'm just going to quit.")
```

### A Beautiful Example

Want to know what a (traffic-less) set of isochrones looks like around the Sears Tower? Behold: 5-, 10-, and 15-minute isochrones.

<center>
<iframe
  width="600"
  height="450"
  frameborder="0" style="border:0"
  src="/html/isochrones/sears_tower_isochrones.html">
</iframe>
</center>

[Note: this is not without erroneous data. I had to go in there and remove a point that somehow ended up in Los Angeles. There are, of course, ways to throw out outliers. That's left as an exercise to the reader.]

Notice how the isochrones aren't regular shapes? They follow the interstate structure and the grid structure primarily, as they should. I think that is just so freakin' cool.

I hope you found this as cool as I did.

Again, you can find my code for this on my github page, [module name is isocronut](https://github.com/drewfustin/isocronut).