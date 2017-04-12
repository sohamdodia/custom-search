#Common module
import urllib2
import json
import pprint

#Server module
from flask import Flask
from flask import request

#Thread module
import threading
import time

#For sending json data
data_json = {}

#Function to search from google
def google_search(query,data_json):
	query = query.replace(" ","+")
	url = 'https://www.googleapis.com/customsearch/v1?key=YOUR_KEY&cx=YOUR_CX&q=' + query
	data = urllib2.urlopen(url)
	data = json.load(data)
	json_data_google = {}
	json_data_google['url'] = data['items'][0]['link']
	json_data_google['text'] = data['items'][0]['snippet']
	# return data_json
	data_json['results']['google'] = json_data_google


#Function to search twitter
def twitter_search(query,data_json):
	# Import the necessary methods from "twitter" library
	from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

	# Variables that contains the user credentials to access Twitter API 
	ACCESS_TOKEN = 'ACCESS_TOKEN'
	ACCESS_SECRET = 'ACCESS_SECRET'
	CONSUMER_KEY = 'CONSUMER_KEY'
	CONSUMER_SECRET = 'CONSUMER_SECRET'

	oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

	# Initiate the connection to Twitter REST API
	twitter = Twitter(auth=oauth)
	json_data_twitter = {}
	try : 	
		# Search for latest tweets 
		data = twitter.search.tweets(q=query,result_type='recent', lang='en', count=1,vertical='default')
		id = data['statuses'][0]['id']
		url = 'https://twitter.com/i/web/status/' + str(id)
		json_data_twitter['url'] = url
		json_data_twitter['text'] = data['statuses'][0]['text']
	except : 
		pass
	
	# return data_json
	data_json['results']['twitter'] = json_data_twitter



#Function to search from duckduckgo
def duckDuckGo_search(query,data_json) : 
	url = 'https://api.duckduckgo.com/?q=' + query + '&format=json&pretty=1'
	data = urllib2.urlopen(url)
	data = json.load(data)
	data_abstractText = (data['AbstractText'])
	json_data_duckDuckGo = {}
	try :
		if len(data_abstractText) > 0 :
			pprint.PrettyPrinter(indent = 5 ).pprint(data['AbstractURL'])
			pprint.PrettyPrinter(indent = 5 ).pprint(data_abstractText)
			json_data_duckDuckGo['url'] = data['AbstractURL']
			json_data_duckDuckGo['text'] = data_abstractText	
		else :
			pprint.PrettyPrinter(indent = 5 ).pprint(data['RelatedTopics'][0]['FirstURL'])
			pprint.PrettyPrinter(indent = 5 ).pprint(data['RelatedTopics'][0]['Text'])
			json_data_duckDuckGo['url'] = data['RelatedTopics'][0]['FirstURL']
			json_data_duckDuckGo['text'] = data['RelatedTopics'][0]['Text']
	except :
		pass
		
	data_json['results']['duckduckgo'] = json_data_duckDuckGo


#Flask Server
app = Flask(__name__)
@app.route("/")
def hello():
	#getting query from url
	query = request.args.get('q') 
	global data_json
	data_json['query'] = query
	data_json['results'] = {}
	
	search_list = [google_search,twitter_search,duckDuckGo_search]
	thread_list = []

	#Creating Threads for functions
	for search in search_list : 
		t = threading.Thread(target = search,args=(query, data_json))
		thread_list.append(t)

	# Starting the thread
	for thread in thread_list :
		thread.start()

	for thread in thread_list :
		thread.join(1)

	results = data_json['results']

	#printing error message according to weather it has response or not.
	for i in ['google', 'twitter', 'duckduckgo']:
		has_key = results.has_key(i);
		if not has_key:
			results[i] = {'error': 'Timed out'}
		elif not results[i].has_key('text'):
			has_key = False
			results[i] = {'error': 'No result'}
		results[i]['status'] = has_key
	json_data = json.dumps(data_json,sort_keys=False,indent=2)
	
	#returing json_data to the client.
	return json_data

if __name__ == "__main__":
	app.run()

		
