import requests,os,bs4
import webbrowser
import sys
import json
import logging
import datetime
import time


site = "http://www.imdb.com/"
genre = "genre/"
choice= "No"
rng = 25
moreVariable = 0
movieIndex = 0
logFile = ""
fileName = ""

imdbDict={1:'upcoming',2: 'genre'}

genreDict ={1: 'Romance', 2: 'Drama', 3: 'Comedies', 4: 'Mystery', 5: 'Fantasy', 6: 'Family', 7: 'Action', 8: 'Thrillers', 9: 'Animation', 10: 'Crime', 11: 'Adventure', 12: 'Music', 13: 'Sci-Fi', 14: 'History', 15: 'Horror', 16: 'Musicals', 17: 'War', 18: 'Biographies', 19: 'Reality-TV', 20: 'Documentaries', 21: 'Sport', 22: 'Game Shows', 23: 'Westerns', 24: 'Talk Shows', 25: 'News', 26: 'Film-Noir', 27: 'Adult'};


def CreateFileNameWithTimeStamp(fileType,Type="IMDB"):
	#Creating Log File Using TimeStamp
	logging.info("Creating File Name Using TimeStamp")
	ts = time.time()
	st = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	fl = Type+st+fileType
	return fl			



logging.basicConfig(filename="log.txt", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')





def Intialization():
	logging.debug("\nStart Initialization\n")
	for k,v in imdbDict.items():
		print(k,v)
	print("Do Enter Index for selecting Genre::")
	logging.info("Do Enter Index for selecting Genre::")
	index = input()
	return index

def IntializationGenre():
	logging.debug("\nStart InitializationGenre\n")
	for k,v in genreDict.items():
		print(k,v)
	print("Do Enter Index for selecting Genre::")
	logging.info("Do Enter Index for selecting Genre::")
	index = input()
	return index

	
def CreateUrl(Choice,GenreType,strMore="Nothing"):
	logging.debug("\nStart CreateUrl\n")
	if Choice == "No":
		print("you have selected "+GenreType+ "  Genre")
		logging.info("you have selected "+GenreType+ "  Genre")
		url = site+genre+GenreType
	else:
		url = site+strMore
	logging.debug("\nReturning From CreateUrl"+url+"\n")
	return url

def GetSoup(url):
	logging.debug("\nStart GetSoup\n")
	res = requests.get(url)
	try:
		res.raise_for_status()
		soup = bs4.BeautifulSoup(res.text)
		return soup
	except requests.exceptions.HTTPError:
		print("Some Problem in GetSoup")
		logging.error("\nException From GetSoup Method\n")
		return " "

def GetRequest(choice,soup):
	logging.info("\n Start GetRequest\n")

	if choice == "Yes":
		comicElem = soup.select('#main .see-more')
		logging.info("\nRequest Using SEE-MORE in Main\n")
	elif choice == "More":
		comicElem = soup.select('#main .pagination')
		logging.info("\nRequest Using PAGINATION in Main\n")
	elif choice == "UpComing":
		comicElem = soup.select('div.aux-content-widget-2 .title')
		logging.info("\nRequest Using Upcoming in Main\n")
	else:
		comicElem = soup.select('#main .title')
		logging.info("\nRequest Using TITLE in Main\n")
	return comicElem

urlList = []

#Unused function, Need to Remove
def findUrl(rangeUrl,listUrl):
	for i in range(rangeUrl):
		logging.info(comicElem[i])
		comicA = listUrl[i].select('a')
		urlList.append(site+comicA[0].get('href'))
	return urlList


def getTitleOfList(Count,Name,Type):
	logging.info("\nStart getTitleOfList\n")
	if Count == 1:
		logging.info(Type+" in "+Name+" is ")
	elif Count > 1:
		logging.info(Type+" in "+Name+" are ")
	else:
		logging.info("There is no " +Type+" in "+Name +".")
		
#Can be modifed to get Genre
def getGenre(CosmicElem,nameMovie,Type=""):
	listCredit = CosmicElem.select('.genre a')
	getTitleOfList(listCredit.count,nameMovie,"Genre")
	for credit in listCredit:
		print(credit.encode('utf-8').strip())

o_actorDict={}
o_genreDict={}

def getCreditGenre(Element,nameMovie,Type=""):
	logging.info("\n Start getCreditGenre method \n")
	typ = '.'+Type
	listCredit = Element.select(typ+' a')
	lst= []
	getTitleOfList(len(listCredit),nameMovie,Type)	
	for credit in listCredit:
		#logging.info(str((credit.getText()).encode('utf-8')))
		lst.append((str(credit.getText().encode('utf-8'))))

		#Adding actors Name and Their Link to Actor Dictionary
		if Type == "credit" and (str(credit.getText().encode('utf-8'))) is not o_actorDict:
			o_actorDict[(str(credit.getText().encode('utf-8')))]=credit.get('href')
		#Adding genres Name and Their Link to Actor Dictionary	
		elif (str(credit.getText().encode('utf-8'))) is not o_genreDict:
			o_genreDict[(str(credit.getText().encode('utf-8')))]=credit.get('href')
	return lst

def getRating(Element,Name):
	logging.info("\n Start getRating method \n")
	lst = Element.select('.user_rating span.rating-rating span')#.rating rating-list span.rating_rating
	rating = ""
	if len(lst) == 0:
		rating = "No"
		logging.info("No Rating for "+Name+" Movie")
	else:
		logging.info(lst[0].getText()+lst[1].getText()+lst[2].getText())
		rating = lst[0].getText()+lst[1].getText()+lst[2].getText()
	return rating

def getOutlineDuration(Element,Name,Type=""):
	logging.info("\n Start getOutlineDurations method \n")
	typ = '.'+Type
	txt = " "
	if len(Element.select(typ))!=0:
		logging.info((Element.select(typ)[0].getText()).encode('utf-8').strip())
		txt = str((Element.select(typ)[0].getText()).encode('utf-8'))
	else:
		txt = "No"
		logging.info("No Information related to "+Type+" is present.")
	return txt

def save(Dict,Type="NO"):
	logging.info("\n Start saveActor method with Type "+Type)

	fl = CreateFileNameWithTimeStamp(".json",Type)
	actor_file = open(fl,"a")
	
	json.dump(Dict,actor_file, indent=4)                                    
	actor_file.close()

startGenreTime = 0
dict={}

def upComing(Site):
	logging.info("Start UpComing Method with input url,choice and rng as "+site)
	soup = GetSoup(Site)
	comicElem = GetRequest("UpComing",soup)
	global movieIndex

	try:
		for i in range(rng):
			comicA = comicElem[i].select('a')
			comicurl = site+comicA[0].get('href')
			print("\n")
			movieIndex += 1
			print(str(movieIndex) +":  "+ comicA[0].getText())
			logging.info("\n"+str(movieIndex) +":  "+ comicA[0].getText()+"\n")
			print("\n")

	except IndexError:
		print("No More Items in UpComing Movie Week")
		main()


def Fetch(url,choice,rng,GenreType):
	logging.info("Start fetch Method with input GenreType, url,choice and rng as "+GenreType+" "+url+" "+choice+" "+str(rng))
	soup = GetSoup(url)
	comicElem = GetRequest(choice,soup)

	tempUrl = ""
	global movieIndex

	try:
		if movieIndex == 500:
			print("Do You Want to Select some Other Genre")
			logging.info("Do You Want to Select some Other Genre??")
			inp = input()
			if inp=="Yes":
				#GOTO Main Function
				main()
			else:
				return
			return

		for i in range(rng):
			comicA = comicElem[i].select('a')
			comicurl = site+comicA[0].get('href')
			print("\n")
			movieIndex += 1
			print(str(movieIndex) +":  "+ str(comicA[0].getText().encode('utf-8')))
			logging.info("\n"+str(movieIndex) +":  "+ str(comicA[0].getText().encode('utf-8'))+"\n")#comicA[0].getText()
			print("\n")
		
	
			name = str(comicA[0].getText().encode('utf-8'))#comicA[0].getText()
			dict["name"]=name
			dict["rating"]=getRating(comicElem[i],name)
			dict["duration"]=getOutlineDuration(comicElem[i],name,"runtime")
			dict["outline"]=getOutlineDuration(comicElem[i],name,"outline")
			dict["genre"]=getCreditGenre(comicElem[i],name,"genre")
			dict["actors"]=getCreditGenre(comicElem[i],name,"credit")
			if len(comicElem[i].select('span.year_type'))!=0:
				logging.info(comicElem[i].select('span.year_type')[0].getText())
				dict["year"]=comicElem[i].select('span.year_type')[0].getText()
			else:
				dict["year"]=""
				logging.info("Year value is not Present for Movie  "+name)

			logging.info(dict.items())
			
			#Creating JSON FILE
			#Creating File Name As per Genre Selected, it can't Use Save as Time stamp will change constantly
			global fileName
			out_file = open(fileName,"a")
			json.dump(dict,out_file, indent=4)                                    
			out_file.close()


	except IndexError:
		print("Maximum Count Reached...Do U want to continue?")
		logging.info("Maximum Count Reached...Do U want to continue?")
		choice = "More"
		#select Next Button Url and choice is by default set to "More" for removing manual entry
		comicEle = GetRequest(choice,soup)
		try:
			
			comic = comicEle[0].select('a')
			global moreVariable
			if moreVariable==0:#Select More Link only
				tempUrl = CreateUrl(choice,GenreType,comic[0].get('href'))
				moreVariable = 1
			else:#If prev and Next Links are present, select Next Link
				tempUrl = CreateUrl(choice,GenreType,comic[1].get('href'))

			Fetch(tempUrl,"No",2*rng+1,GenreType)

		except Exception:
			print("Please do Return to Main")
			main()

		
def goToShowMore(url,GenreType):
	#Checking Show-More Option here choice is "Yes"
	soup = GetSoup(url)
	comicEle = GetRequest("Yes",soup)
	#Goto Show More and Start here choice is "Yes"
	if ((comicEle[0].select('a'))[0].getText())=="show more":
		comic = comicEle[0].select('a')
		#Change the url Value to Link of Show-More Href
		tempurl = CreateUrl("Yes",GenreType,comic[0].get('href'))
		global rng
		rng = 2 * rng
	else:
		tempurl = url

	return tempurl
	
def fetchUtil(GenreType):
	url = CreateUrl(choice,GenreType)
	print(url)	
	#Check for Show-more or Return base url
	url = goToShowMore(url,GenreType)
	Fetch(url,choice,rng+1,GenreType)

def main():
	temp = Intialization()
	
	#Need to be updated as movie index needs to be reset after choosing different genre/type 
	global movieIndex
	movieIndex = 0

	#Needs To be Reset for New genre/type as first time only Next is present
	global moreVariable
	moreVariable = 0

	
	if imdbDict.get(int(temp)) == 'genre':
		startGenreTime = time.time()
		#global Index
		Index = IntializationGenre()

		global fileName
		fileName = genreDict[int(Index)]
		
		fetchUtil(fileName)
	else:
		print("Looking For Some UpComing Movies In Coming Week"+site)
		logging.info("Looking For Some UpComing Movies In Coming Week"+site)
		upComing(site)

if __name__ == "__main__":
	main()	
	save(o_actorDict,"Actor")
	save(o_genreDict,"Genre")


