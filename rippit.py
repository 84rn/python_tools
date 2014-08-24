from lxml import html
import os
import argparse
import urllib
import re

# TODO:
#   - divide requests into threads
#   - define FINISH argument when -pe is not provided
#   - check if not overwriting, ask user if should (Y/N/A)
#   - add parameter that forces overwriting
#   - check for errors: page load, img retrieve

parser = argparse.ArgumentParser(description='Batch-download pictures from a subreddit.')
parser.add_argument("subreddit", help="name of the subreddit from which you want to rip")
parser.add_argument("-ps", help="start page (default: 0)", metavar='#', default=0, type=int)
parser.add_argument("-pe", help="end page", metavar='#', default=0, type=int)
parser.add_argument("-d",  help="directory for the pictures (default: current dir)", metavar='dir', default='.')
parser.add_argument("-t",  help="time window (default: day)", \
                    choices=['day', 'week', 'month', 'year', 'all'], default='day')
parser.add_argument("-s",  help="sorting method (default: hot)", \
                    choices=['new', 'hot', 'top'], default='hot')
parser.add_argument("-f", "--force",  help="force overwriting", action="store_true")
parser.add_argument("-v", "--verbose", help="show additional information", action="store_true")
args = parser.parse_args()

p_start = args.ps
p_end = args.pe
save_dir = os.path.normpath(args.d)
if not os.path.isdir(save_dir):
    print 'Creating ' + save_dir
    os.makedirs(save_dir)
    
time_window = args.t
sorting = args.s
subreddit = args.subreddit

def getRootUrl(subreddit, time, sort):
    return 'http://imgur.com/r/' + subreddit + '/' + sort + '/' + time + '/'

def getPagedUrl(url, page):
    return url + 'page/' + str(page)

def replaceIllegalChars(s):
    return re.sub('[\?\*\\/\:\<\>\|\"]', "", s, 0, 0).replace(' ', '_')

rootUrl = getRootUrl(subreddit, time_window, sorting)

num_pics = 1
for p in range(p_start, p_end):
    print 'Opening page ' + str(p + 1) + ' (of ' + str(p_end) + ')'
    page = urllib.urlopen(getPagedUrl(rootUrl, p))
    source = page.read()
    tree = html.fromstring(source)
    imglist = tree.xpath('//*[@id="imagelist"]/div[1]')
    num = len(imglist[0]) - 2
    for i in range(0, num):
        img_element = imglist[0][i][0][0]
        desc_element = imglist[0][i][1][0]
        type_element = imglist[0][i][1][1]
        type_text = type_element.text.strip()[:5]      
        img_url = img_element.get("src")
        desc = replaceIllegalChars(desc_element.text)[:128].encode('ascii', 'ignore')                       
        img_url = 'http:' + img_url[:-5] + img_url[-4:]
        type = 'gif'
        if(type_text == 'image'):
            type = 'jpg'
        filename = desc + '.' + type
        save_path = save_dir + '\\' + filename
        if args.verbose:
            print 'Saving [' + str(num_pics) + '] ' + filename
        if(os.path.exists(save_path)):
            print 'File \'' + filename + '\' already exists. Overwrite? [Y/N/A]'
        urllib.urlretrieve(img_url, save_path)
        num_pics = num_pics + 1
print 'Finished saving ' + str(num_pics - 1) + ' pictures from ' + str(p_end - p_start) + ' page(s).'
