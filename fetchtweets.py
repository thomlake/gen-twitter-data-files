import signal, socket, base64, sys, json, time, threading, urllib2, Queue
import foreignwords

SLEEP_TIME_INIT = 0.2
SLEEP_TIME_THROTTLE = 4.0
TIMEOUT_DURATION = 6.0
MAX_SLEEP_TIME = 240.0
WAIT_TIME = 4.0


USR = ''
PWD = ''

def timeout(func, args = [], duration = 2.0):
	class TimeoutThread(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.result = None
		def run(self):
			try:
				self.result = func(*args)
			except:
				self.result = None
	tothread = TimeoutThread()
	tothread.start()
	tothread.join(duration)
	if tothread.isAlive():
		return None
	else:
		return tothread.result

def cleanse(text):
	return text.replace('\n', ' ').replace('\r', ' ')

def probably_english(text):
	text = text.lower()
	for c in text:
		o = ord(c)
		if o < ord(' ') or o > ord('~'):
			return False
	for word in foreignwords.words:
		if word in text:
			return False
	return True

def producer(request, q, run_flag):
	time_to_sleep = SLEEP_TIME_INIT
	count = 0
	while len(run_flag) == 0:
		try:
			print 'PRODUCER > making request'
			f = urllib2.urlopen(request)
			print 'PRODUCER > request done, reading from socket'
			line = timeout(f.readline, duration = TIMEOUT_DURATION)
			while line:
				if len(run_flag) == 0:
					q.put(line)
					line = timeout(f.readline, duration = TIMEOUT_DURATION)
				else:
					line = None
					f.close()
					return
			time_to_sleep = SLEEP_TIME_INIT
		except (urllib2.URLError, urllib2.HTTPError), e:
			print >> sys.stderr, 'PRODUCER > Exception: %s, retry in %f' %(e, time_to_sleep)
			time.sleep(time_to_sleep)
			time_to_sleep *= SLEEP_TIME_THROTTLE
			if time_to_sleep > MAX_SLEEP_TIME:
				time_to_sleep = MAX_SLEEP_TIME
		except Exception as err:
			print >> sys.stderr, 'PRODUCER > Exception: %s' %(err)

def consumer(q, fout, run_flag):
	buff = ''
	print 'CONSUMER > starting'
	while len(run_flag) == 0:
		try:
			if not q.empty():
				while not q.empty():
					item = q.get()
					buff += item
					if item.endswith('\r\n') and item.strip():
						json_result = json.loads(buff)
						buff = ''
						try:
							lang = json_result['user']['lang']
							text = json_result['text']
							if lang == 'en':					# only english (not sufficient)
								if not text.startswith('RT'):	# no retweets
									text = cleanse(text)		# strip '\n' & '\r'
									if probably_english(text):	# foreign words and ascii val
										try:
											print >> fout, text
										except UnicodeEncodeError as err:
											print >> sys.stderr, 'CONSUMER > Exception: %s' %(err)
						except KeyError as err:
							pass
		except Exception as err:
			print >> sys.stderr, 'Consumer > Exception: %s' %(err)
		time.sleep(WAIT_TIME)


def main():
	q = Queue.Queue()
	run_flag = []
	log = open('fetch.log', 'w')
	#sys.stderr = log
	#sys.stdout = log
	fout = open('tweets.txt', 'w')
	print 'MAIN > starting'
	auth = base64.encodestring('%s:%s' %(USR, PWD))[:-1]
	authheader = 'Basic %s' %(auth)
	twitter_req = urllib2.Request('http://stream.twitter.com/1/statuses/sample.json')
	twitter_req.add_header('Authorization', authheader)
	consumer_thread = threading.Thread(target = consumer, args = (q, fout, run_flag))
	try:
		consumer_thread.start()
		producer(twitter_req, q, run_flag)
		# should never get here
		run_flag.append(False)
		consumer_thread.join()
	except KeyboardInterrupt:
		run_flag.append(False)
		consumer_thread.join()
		fout.close()
		log.close()
		sys.exit()


if __name__ == '__main__':
	USR = sys.argv[1]
	PWD = sys.argv[2]
	main()
