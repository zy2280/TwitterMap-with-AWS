# coding: utf-8
#from urllib.request import urlopen
import json
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

import oauth2
import json

from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import requests
from flask import Flask, render_template, request

from random import randint
import random

from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth



AWS_ACCESS_KEY='key'
AWS_SECRET_KEY='secrete'
region = 'us-east-2' 
service = 'es'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

host = 'search-twitter-za3cvpj2uasrtoy7lfjzvrrqqq.us-east-2.es.amazonaws.com' 
es = Elasticsearch(
		hosts=[{'host': host, 'port': 443}],
		http_auth=awsauth,
		use_ssl=True,
		verify_certs=True,
		connection_class=RequestsHttpConnection,
		request_timeout=100
	)


	
def get_tweets_from_es(word, lat, lng, distance):

	es.indices.refresh(index="twitter3")
	res = es.search(index="twitter3", body=      {
    "query": {
        "bool" : {
            "must" : {
                "match": {"text":word}
            },
            "filter" : {
                "geo_distance" : {
                    "distance" : distance,
                    "location": [lng, lat]
                        
 

                    }
                }
            }
        }
    }, size=5000)

	text = []
	image = []
	location = []
	user = []
	
	for hit in res['hits']['hits']:
		text.append(hit["_source"]['text'])
		image.append(hit["_source"]['profile'])
		location.append({"lng": hit["_source"]['location'][0], "lat": hit["_source"]['location'][1]})
		user.append(hit["_source"]['user_name'])
		
	return [text, image, location, user]	



application = Flask(__name__)
application.debug=True

application.secret_key = 'K3JDpmz2Com38BlBf58keeVws'

@application.route('/Home', methods= ['POST','GET'])
def home():
	if request.method == "POST":
		word = request.form['text']
		lat = request.form['Lat']
		lng = request.form['Lng']
		distance = ''.join([request.form['distance'], "km"])
		dist = str(float(request.form['distance']) * 1000)
		center_location = {'lat': float(lat), 'lng': float(lng)}	
		output = get_tweets_from_es(word, float(lat), float(lng), distance)

		lst = []	

		for tw in output[0]:
			lst.append(''.join([tw, "|"]))

		tweets = lst 
		image = output[1] 
		location = output[2]
		name = output[3] 
		count = len(tweets)
 
			
		return render_template("test.html", center = center_location, lat_lng = location, tweet= tweets, user= name, profile= image, x = count, D = dist)
	else:
		return render_template('index.html')	



if __name__ == "__main__":
	application.debug = True
	application.run()
