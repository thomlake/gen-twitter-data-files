import tweepy, sys

class StreamController:
	def __init__(self, uname, pword, fname = "samp-out.txt"):
		self.n = 100000 #number of samples
		self.ofile = open(fname, "w")
		self.handler = StreamHandler(self)
		self.stream = tweepy.Stream(uname, pword, self.handler, timeout=None)

		self.ctr = 0
		self.tweetlist = []

	def is_standard_ascii(self, text):
		for c in text:
			if c > '~':
				return False
		return True
	
	def handle_tweet(self, tweettext):
		if self.is_standard_ascii(tweettext):
			tweettext = tweettext.replace('\n', ' ')
			self.ctr += 1		
			self.ofile.write(tweettext.encode("iso-8859-1", "ignore") + "\n")
	
	def start_sample(self):
		self.stream.sample()
	
	def stop_sample(self):
		self.stream.disconnect()
		for i, twit in enumerate(self.tweetlist):
			print i, ":", twit

class StreamHandler(tweepy.StreamListener):
	def __init__(self, controller = None):
		super(StreamHandler, self).__init__()
		self.controller = controller
	
	def on_status(self, status):
		if self.controller.ctr < self.controller.n:
			if status.author.lang == "en":
				self.controller.handle_tweet(status.text)
		else:
			self.controller.stop_sample()

if __name__ == "__main__":
	if len(sys.argv) < 3 or len(sys.argv) > 4:
		print "usage: tweepstream.py  req(username) req(password) opt(filename)"
		sys.exit()
	twit = None
	uname = sys.argv[1]
	pword = sys.argv[2]
	if len(sys.argv) == 4:
		fname = sys.argv[3]
		twit = StreamController(uname, pword, fname)
	else:
		twit = StreamController(uname, pword)
	twit.start_sample()
