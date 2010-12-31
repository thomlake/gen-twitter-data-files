import json, urllib2, sys
from collections import deque

def is_standard_ascii(text):
	for c in text:
		if c > '~':
			return False
	return True


def search(searchword, fname = "search-out.txt", numsamples = 1500):
	searchword = searchword
	ctr = 0
	ofile = open(fname, "w")
	page = 1
	last100tweets = deque([])
	while ctr < numsamples and page <= 100:
		url = urllib2.urlopen("http://search.twitter.com/search.json?q=" + searchword + "&page=" + str(page))
		json_response = json.load(url)
		page += 1
		for response in json_response["results"]:
			try:
				if response["iso_language_code"] == "en":
					tweet = response['text']
					if len(tweet.split("RT")) > 1:
							continue
					if is_standard_ascii(tweet):
						if tweet in last100tweets:
							continue
						last100tweets.append(tweet)
						last100tweets.popleft()
						ofile.write(tweet.encode("iso-8859-1", "ignore") + "\n")
						ctr += 1
			except:
				print "EXCEPTION", sys.exc_info()[0]
				print "in:", response
				pass

def is_standard_ascii(text):
	for c in text:
		if ord(c) > ord('~'):
			return False
	return True

if __name__ == "__main__":
	if len(sys.argv) < 2 or len(sys.argv) > 3:
		print "usage: searchsample.py req(search word) opt(filename)"
		sys.exit()
	searchword = sys.argv[1]
	if len(sys.argv) == 3:
		fname = sys.argv[2]
		search(searchword, fname)
	else:
		search(searchword)
