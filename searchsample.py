import json, urllib2, sys


def search(searchword, fname = "search-out.txt", numsamples = 1500):
	searchword = searchword
	n = numsamples
	ctr = 0
	ofile = open(fname, "w")
	page = 1
	while ctr < numsamples:
		url = urllib2.urlopen("http://search.twitter.com/search.json?q=stuff&page=" + str(page))
		json_response = json.load(url)
		page += 1
		for response in json_response["results"]:
			ctr += 1
			try:
				if response["iso_language_code"] == "en":
					tweet = response['text']
					print tweet
					ofile.write(tweet.encode("iso-8859-1", "ignore") + "\n")
			except:
				pass

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
