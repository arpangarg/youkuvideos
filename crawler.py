import urllib
from requests import get
from lxml import html
import logging
import re


class Crawler(object):

	def __init__(self):
		logging.getLogger("requests").setLevel(logging.WARNING)
		logging.basicConfig(filename='crawl.log', level=logging.DEBUG)

		self.file_out = open('output.txt', 'w')

		self.url = (
			'http://www.soku.com/search_video/q_{0}_orderby_1_limitdate_0?'
			'site=14&page={1}'
		)

		self.video_url = 'http://v.youku.com/v_show/{0}.html'

	def do_crawl(self):
		videos = set()

		utf_start = 19968
		utf_end = 40918

		for i in range(utf_start, utf_end):
			uni_char = unichr(i)
			encoded = uni_char.encode('utf-8')
			url_encoded = urllib.urlencode({'a':encoded})[2:]

			page = 0

			while(True):
				page += 1
				complete_url = self.url.format(url_encoded, page)

				try:
					response = get(complete_url)
				except:
					logging.warning(
						'unable to complete request for ' + complete_url
					)

				tree = html.fromstring(response.content)

				raw_links = tree.xpath(
					"//div[@class='v-meta va']/div[@class='v-meta-title']/"
					"a/@href"
				)

				for link in raw_links:
					found = re.search('v_show\/(.+).html', link)

					if found:
						short_link = found.group(1)
						if short_link not in videos:
							videos.add(short_link)
							self.file_out.write(
								self.video_url.format(short_link) + '\n'
							)
					else:
						logging.warning('regex did not work on ' + link)

				if not raw_links or page == 100:
					break;

				if page % 10 == 0:
					logging.info(
						url_encoded + ' Visited ' + str(page*20) + ' urls ' + \
						'found total unique ' + str(len(videos))
					)


if __name__ == "__main__":
	c = Crawler()

	c.do_crawl()
