import lxml.html
from lxml.cssselect import CSSSelector
import requests

def remove_duplicates(lst):
	already_in = {}
	new = []
	for i in lst:
		try:
			already_in[i]
		except KeyError:
			new.append(i)
			already_in[i] = 5
	return new

def find_site(name):
	links = []
	good_links = []
	url = "http://google.com/search?q=" + str(name)
	r = requests.get(url=url)

	res = r.text
	res_list = res.split("&amp;")
	for link in res_list:
		if 'href="/url?q=' in link:
			link = link.split('href="/url?q=')[1]
			if 'googleusercontent' not in link:
				links.append(link)
	for link in links:
		if not (link[-1:] == "/" and link.count("/") > 3) and not (link[-1:] != "/" and link.count("/") > 2):
			good_links.append(link)

	return remove_duplicates(good_links)

def is_in(site, item):
	item = item.lower()
	url = find_site(site)[0]
	x = requests.get(url).text.lower()
	if not ">" + item + "<" in x and not " " + item + " " in x:
		print x
		return False
	parts = x.split(" " + item + " ")
	if len(parts) < 2:
		parts = x.split(">" + item + "<")
		if len(parts) < 2:
			return False
	first = parts[0].split(" ")[-1]
	if ">" in first:
		first = first.split(">")[-1]
	elif '"' in first:
		first = first.split('"')[-1]
	second = parts[1].split(" ")[0]
	if "<" in second:
		second = second.split("<")[0]
	elif '"' in second:
		second = second.split('"')[-1]
	to_return = first + " " + item + " " + second
	to_return = to_return.replace("&nbsp;", " ")
	to_return = to_return.strip()
	if to_return[-1] == ">" or to_return[-1] == "<":
		to_return = to_return[:-1]
	if to_return[-1] == '"' or to_return[-1] == "'":
		to_return = to_return[:-1]
	if to_return[0] == ">" or to_return[0] == "<":
		to_return = to_return[1:]
	if to_return[0] == '"' or to_return[0] == "'":
		to_return = to_return[1:]
	return to_return

def parse_twitter(parts):
	if len(parts) != 2:
		return -1
	amount = parts[1].split('"')[0]
	amount = amount.replace(",", "")
	return int(amount)

def parse_twitter_for_follower_count(txt):
	parts = txt.split('Followers<strong title="')
	return parse_twitter(parts)

def parse_twitter_for_tweet_count(txt):
	parts = txt.split('Tweets<strong title="')
	return parse_twitter(parts)

def parse_twitter_for_following_count(txt):
	parts = txt.split('Following<strong title="')
	return parse_twitter(parts)

def more_followers(user_a, user_b):
	a = requests.get("http://twitter.com/" + user_a).text
	a_count = parse_twitter_for_follower_count(a)
	b = requests.get("http://twitter.com/" + user_b).text
	b_count = parse_twitter_for_follower_count(b)
	if a_count > b_count:
		return user_a
	else:
		return user_b

def more_tweets(user_a, user_b):
	a = requests.get("http://twitter.com/" + user_a).text
	a_count = parse_twitter_for_tweet_count(a)
	b = requests.get("http://twitter.com/" + user_b).text
	b_count = parse_twitter_for_tweet_count(b)
	if a_count > b_count:
		return user_a
	else:
		return user_b

def more_following(user_a, user_b):
	a = requests.get("http://twitter.com/" + user_a).text
	a_count = parse_twitter_for_following_count(a)
	b = requests.get("http://twitter.com/" + user_b).text
	b_count = parse_twitter_for_following_count(b)
	if a_count > b_count:
		return user_a
	else:
		return user_b

def get_number_of_retweets(tweet_url):
	r = requests.get("http://twitter.com" + tweet_url).text
	if 'data-activity-popup-title="Retweeted ' in r:
		parts = (r.split('data-activity-popup-title="Retweeted ')[1]).split(" ")
		return int(parts[0])
	else:
		return 0

def get_number_of_favorites(tweet_url):
	r = requests.get("http://twitter.com" + tweet_url).text
	if 'data-activity-popup-title="Favorited ' in r:
		parts = (r.split('data-activity-popup-title="Favorited ')[1]).split(" ")
		return int(parts[0])
	else:
		return 0

def get_most_recent_tweet(user):
	r = requests.get("http://twitter.com/" + user).text
	tree = lxml.html.fromstring(r)
	sel = CSSSelector('ol#stream-items-id li div.stream-item-header small.time a')
	results = sel(tree)
	match = results[0]
	return match.get('href')

def get_hn_karma(user):
	r = requests.get("https://news.ycombinator.com/user?id=" + user).text
	karma = (r.split('<tr><td valign=top>karma:</td><td>')[1])
	karma = karma.split("</td></tr>")[0]
	return int(karma)

def get_hn_age(user):
	r = requests.get("https://news.ycombinator.com/user?id=" + user).text
	karma = (r.split('<tr><td valign=top>created:</td><td>')[1])
	karma = karma.split(" day")[0]
	return int(karma)

def older_hn(user_a, user_b):
	a = get_hn_age(user_a)
	b = get_hn_age(user_b)
	if a > b:
		return user_a
	else:
		return user_b

def higher_karma_hn(user_a, user_b):
	a = get_hn_karma(user_a)
	b = get_hn_karma(user_b)
	if a > b:
		return user_a
	else:
		return user_b

def get_reddit_karma(user):
	r = requests.get("http://www.reddit.com/user/" + user).text
	link_karma = ((r.split('<span class="karma">')[1]).split("</span>")[0]).replace(",","")
	comment_karma = ((r.split('<span class="karma comment-karma">')[1]).split("</span>")[0]).replace(",","")
	return int(link_karma) + int(comment_karma)

def higher_karma_reddit(user_a, user_b):
	a = get_reddit_karma(user_a)
	b = get_reddit_karma(user_b)
	if a > b:
		return user_a
	else:
		return user_b

def get_iron_pants_rank(uuid):
	data = {}
	data["taskai"] = "null"
	data["toLoad"] = "daily"
	data["uid"] = uuid
	data["isConnectedTrue"] = "pjjklnbs68"
	data["submitName"] = "null"
	r = requests.post("http://www.ringas.lt/ironpants/highscores.php", data=data)
	parts = r.text.split("&")
	for p in parts:
		if p.startswith("kelintas"):
			return int(p.split("=")[1])

def higher_high_score(uuid_a, uuid_b):
	a = get_iron_pants_rank(uuid_a)
	b = get_iron_pants_rank(uuid_b)
	if a > b:
		return user_a
	else:
		return user_b

def main():
	# print is_in(raw_input("Enter site: "), raw_input("Enter text: "))
	# print more_followers(raw_input("Person a: "), raw_input("Person b: "))
	# username = raw_input("Enter Twitter handle: ")
	# try:
	# 	most_recent = get_most_recent_tweet(username)
	# 	print "Favorites:", get_number_of_favorites(most_recent)
	# 	print "Retweets:", get_number_of_retweets(most_recent)
	# except IndexError:
	# 	print
	# try:
	# 	print "HN Karma:", get_hn_karma(username)
	# except IndexError:
	# 	print
	user_a = raw_input("Enter user_a: ")
	user_b = raw_input("Enter user_b: ")
	try:
		print "More karma:",higher_karma_hn(user_a, user_b)
		print "Older user:",older_hn(user_a, user_b)
	except IndexError:
		print
	try:
		print "Higher karma:", higher_karma_reddit(user_a, user_b)
	except IndexError:
		print

if __name__ == "__main__":
	main()