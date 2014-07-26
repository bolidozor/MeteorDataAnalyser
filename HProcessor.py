
from HTMLParser import HTMLParser
from urllib import urlopen
import pandas as pd
import urllib
import matplotlib.pyplot as plt


def get_data(url_meteors, x):
    
    ArrayHTML = []
    ahtml2=[]
    ahtml3=[]

    class MyHTMLParser(HTMLParser):
	    global ArrayHTML
	    global ahtml2
	    global ahtml3
	    def handle_data(self, data):
		    ahtml3.append(data)
	    def handle_starttag(self, tag, attrs):
		    if tag == "a":
			    for name, value in attrs:
				    ArrayHTML.append(value)
				    ahtml2.append(name)
    murl = url_meteors
    html = urlopen(url_meteors).read()

    parser = MyHTMLParser()
    parser.feed(html)
    ArrayHTML=ArrayHTML[1:]


    ahtml4=[]
    ahtml6=[]
            
    for link in ahtml3:
        if '\n' not in link and 'Index' not in link and 'Parent' not in link:
            ahtml6.append(link)
            

    nurl=murl+ahtml6[-1][1:]

    html = urlopen(nurl).read()

    parser = MyHTMLParser()
    parser.feed(html)
    ArrayHTML=ArrayHTML[1:]


    ahtml4=[]
    ahtml6=[]
         
    for link in ahtml3:
        if '\n' not in link and 'Index' not in link and 'Parent' not in link:
            ahtml6.append(link)
            
    xnurl=nurl+ahtml6[-1][1:]

    html = urlopen(xnurl).read()

    parser = MyHTMLParser()
    parser.feed(html)
    ArrayHTML=ArrayHTML[1:]


    ahtml4=[]
    ahtml6=[]
         
    for link in ahtml3:
        if '\n' not in link and 'Index' not in link and 'Parent' not in link:
            ahtml6.append(link)
            
            
    anurl=xnurl+ahtml6[-1][1:]
    html = urlopen(anurl).read()

    parser = MyHTMLParser()
    parser.feed(html)
    ArrayHTML=ArrayHTML[1:]

    ahtml4=[]
    ahtml6=[]

    for link in ahtml3:
        if link[-3:]=="csv":
            ahtml4.append(link)
            
    ahtml41=ahtml4
    ahtml7=[]   
    ahtml3=[]     
            
            
    if len(ahtml4)<x:
        aanurl=anurl[:-3]
        html = urlopen(aanurl).read()
        parser = MyHTMLParser()
        parser.feed(html)
        ArrayHTML
        ArrayHTML=ArrayHTML[1:]
        for link in ahtml3:
            if '\n' not in link and 'Index' not in link and 'Parent' not in link:
                ahtml6.append(link)
        aaanurl=aanurl+ahtml6[-2][1:]
        html = urlopen(aaanurl).read()
        parser = MyHTMLParser()
        parser.feed(html)
        ArrayHTML=ArrayHTML[1:]
        for link in ahtml3:
            if link[-3:]=="csv":
                ahtml7.append(link)
        ahtml4=ahtml4+ahtml7[-(x-len(ahtml41)):]
        listret=[ahtml4, ahtml7, anurl, aaanurl]
        return listret
    else:
        aaanurl=[]
        return [ahtml4, ahtml7, anurl, aaanurl]
        

def get_values(url_meteors, x):
    get_data(url_meteors, x)
    list_returned=get_data(url_meteors, x)

    
    [ahtml4, ahtml7, anurl, aaanurl]=list_returned
    
    data=[]       
    for filename in list_returned[0]:   
        if filename in ahtml7:
            data.append(pd.read_csv(aaanurl + filename[1:], names = ["a", "b", "c", "d", "e"], sep = ";"))
        else:
            data.append(pd.read_csv(anurl + filename[1:], names = ["a", "b", "c", "d", "e"], sep = ";"))  
            
    freq_data = []

    for f in range(len(data)):   
        x=[int(round(i)) for i in data[f]["c"]]
        freq_data=freq_data+x
    return freq_data

def process_histogram(url_meteors, x):
    plt.hist(get_values(url_meteors, x), bins=100)
    plt.title("Histogram for observations in the past six hours") #change title if necessary
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Count")
    plt.show()

#process_histogram("http://space.astro.cz/bolidozor/OBSUPICE/OBSUPICE-R1/data/", 6)

