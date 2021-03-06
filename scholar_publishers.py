# Classes for crawling publishers with scholar.py

from selenium import webdriver
from bs4 import BeautifulSoup as Soup
import warnings
import pandas as pd
import re, os
from urllib import urlretrieve

class publisher():
    def __init__(self,PAPER_URL):
        # initialize crawler
        self.browser = webdriver.Chrome() 
        self.browser.get(PAPER_URL)
        source = self.browser.page_source
        warnings.filterwarnings('ignore')
        self.soup = Soup(source,'lxml')

    def close_browser(self):
        self.browser.close()
        
    def download_img(self, img_url_list, paper_dir):
        # download images to local files
        for img_url in img_url_list:
            urlretrieve(img_url, paper_dir+str(img_url.split('/')[-1]))

class ieee(publisher):   
    # IEEE proceedings. last tested May 16, 2016
    def get_img_url(self):
        # Get URLs of images embedded in page
        IEEE_IMG_PREFIX = 'http://ieeexplore.ieee.org'
        img_a_href = self.soup.findAll('a')
        img_url_list = []
        for i in img_a_href:
            if i.has_key('href'):
                href = i['href'].split('/')
                if 'img' in href and ('large.gif' in href[-1].split('-')): # get large hi-res images
                    img_url_list.append(IEEE_IMG_PREFIX + i['href'])
        return list(set(img_url_list))
    
    def get_title_abstract(self):
        """HZ updated 03/03/2017""" ###YW updated 03/07 
      
        abstracts = self.soup.findAll(attrs={"class" : "abstract-text ng-binding"})
        if len(abstracts) == 1:
            abstract = str(abstracts[0])
        print 'abstract:', abstract
        abstract = abstract.strip('<div class="abstract-text ng-binding" ng-bind-html="::vm.details.abstract">')
        abstract = abstract.strip('</')
        print abstract
        divs = self.soup.findAll(['div'])
        for div in divs:
            if div.has_key('class') and div['class'][0]=='document-title-container':
                title = re.split('<h1 class="document-title">|<!-- ngIf: vm.titleContainsRedline -->', str(div))[1]
                break
        return title, abstract

    def get_fullbody(self):
        div_tags=self.soup.findAll("div")
        fullbody=""
        print len(div_tags)
        for div in div_tags:
                #if div.has_key('id') and div['id']=='BodyWrapper':
                    pragraph = str(div)
                    fullbody =fullbody+pragraph+"\n"
        return fullbody
        # print 'length of divs', len(divs)

        
class ScienceDirect(publisher):
    # Elsevier, including composite science and tech, polymer
    # Last tested: May 18, 2016  ### update 03/09/17 -Yixing; new publushed journal has different structure
    def get_title_abstract(self):
        h1 = self.soup.findAll('h1')
        title = re.split('>|</h1>', str(h1[0]))[1]

        div_p_tags = self.soup.findAll(['div', 'p'])
        ind = 0
        for div in div_p_tags:
            if div.has_key('class') and div['class'][0] == 'abstract' and div['class'][1] =='svAbstract':
                abstract_ind = ind + 1
                break
            ind += 1
        abstract = re.split( '<p id="">|</p>', str(div_p_tags[abstract_ind]))[1]
        if len(abstract)==0:
            abstract = re.split( '<p id="sp005">|</p>', str(div_p_tags[abstract_ind]))[1]
        if len(abstract)==0:
            abstract = re.split( '<p id="sp0005">|</p>', str(div_p_tags[abstract_ind]))[1]
        if len(abstract)==0:
            abstract = re.split( '<p id="abspara0010">|</p>', str(div_p_tags[abstract_ind]))[1]
        return title, abstract
    def get_fullbody(self):
        p_tags=self.soup.findAll('p')
        fullbody = ""
        for p in p_tags:
            if p.has_key('class') and p['class'][0] == 'svArticle':
                pragraph = re.split('<p class="svArticle section clear" id="">|</p>', str(p))[1]
                fullbody =fullbody+pragraph+"\n"
        return fullbody
    def get_img_url(self):
        a_tags = self.soup.findAll('a')
        img_url_list = []
        for a in a_tags:
            if a.has_key('class') and a['class'][0]=='ppt':
                img_url_list.append(a['href'])
        return img_url_list
    
    def download_img(self, img_url_list, paper_dir):
        # download image ppt files to local files
        for img_url in img_url_list:
            urlretrieve(img_url, paper_dir+str(img_url.split('/')[-2])+'.ppt')
            
class acs(publisher):
    # ACS. Last tested May 18, 2016
    def get_title_abstract(self):
        span_tags = self.soup.findAll('span')
        for span in span_tags:
            if span.has_key('class') and span['class'][0]=='hlFld-Title':
                title = re.split('<span class="hlFld-Title">|</span>', str(span))[1]
                break
        p_tags = self.soup.findAll('p')
        for p in p_tags:
            if p.has_key('class') and p['class'][0]=='articleBody_abstractText':
                abstract = re.split('<p class="articleBody_abstractText">|</p>', str(p))[1]
                break
        return title, abstract
    
    def get_img_url(self):
        scripts = self.soup.findAll('script')
        # define namespace of string for string evaluation
        doi = 'doi'
        path = 'path'
        i = 'i'
        m = 'm'
        l = 'l'
        g = 'g'
        figures = 'figures'
        ACS_IMG_PREFIX = 'http://pubs.acs.org'
        img_url_list = []
        for script in scripts:
            script_content = re.split('<script type="text/javascript">|</script>', str(script))[1]
            if 'window.figureViewer' in script_content:
                # remove whitespace and return character 
                script_no_space = [char for char in script_content if char not in [' ', '\n']]
                # concatenate characters to new string
                script_str = ''
                for char in script_no_space: 
                    script_str += char
                script_str = script_str[len('window.'):] # strip 'window.' from the beginning of string
                script_dict = eval(script_str.split('=')[1])
                for fig in script_dict[figures]:
                    print fig[g][0].keys()
                    fig_name = fig[g][0][l]
                    img_url = ACS_IMG_PREFIX+ script_dict[path] + '/images/large/'+fig_name
                    img_url_list.append(img_url)
                break
        return img_url_list
    
class aip(publisher):
    # AIP. Last tested 06/08/2016 Updated 03/07/17-YIxing
    def get_title_abstract(self):
        div_tags = self.soup.findAll('div')
        #print len(div_tags),type(div_tags)
        for div in div_tags:
            if div.has_key('class') and div['class'][0]=='hlFld-Title':
                title = re.split('<h2>|</h2>', str(div))[1]
                #print 'title is',title
                break
        for div in div_tags:
            if div.has_key('class') and div['class'][0]=='NLM_paragraph':
                abstract = re.split('<div class="NLM_paragraph">|</div>', str(div))[1]
                print abstract
                #print 'abstract is',abstract
                break
        return title, abstract        
    def get_fullbody(self) 
class rsc(publisher):
    # RSC. 06/08/2016
    def get_title_abstract(self):
        meta_tags = self.soup.findAll('meta')
        print '---'
        for meta in meta_tags:
            if meta.has_key('name') and meta['name']=='DC.title':
                title = meta['content']
                break
        p_tags = self.soup.findAll('p')
        for p in p_tags:
            if p.has_key('class') and p['class'][0]=='abstract':
                abstract = re.split('<p class="abstract">|</p>', str(p))[1]
                break
        title = title.encode('utf8', 'replace')
        print title
        print '---'
        # abstract = abstract.encode('utf8', 'replace')
        print abstract
        return title, abstract