# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
'''
Created on 02 Jan 2016

@author: Seko
@summary: Template for source class

'''
#---------------------------------------------------------------------
# ____________________        I M P O R T        ____________________
import xbmc
import sys
import re
import strUtil
import webUtil
from BeautifulSoup import BeautifulSoup
from src_mod.sourceTemplate import streamingSourceTemplate as Source
from item import StreamItem
from logger import Logger

if sys.argv[0].endswith('test.py'):
    import resources.lib.test.dummyMiscFunctions as miscFunctions
else:
    import miscFunctions as miscFunctions

# ____________________        C L A S S          ____________________
class Fullmoviz(Source):
    """
        @todo: Ajouter method getmoviesbygenre
    """
    
    # ___ The source ID
    ID = 4
    
    # ___ The name of the source
    NAME = 'Fullmoviz'
    
    # WEB PAGE BASE
    WEB_PAGE_BASE = "http://www.fullmoviz.org/"
    
    # LOGGER    
    __LOGGER__ = Logger('UltraStream','Fullmoviz')
    
    # MENU
    
    MAIN_MENU_OPT = [#Source.MAIN_MENU_MOVIE_HD,
                     Source.MAIN_MENU_MOVIE,
                     #Source.MAIN_MENU_TVSHOW,
                     #Source.MAIN_MENU_ANIME,
                     #Source.MAIN_MENU_SHOW,
                     #Source.MAIN_MENU_DOCUMENTARY]
                     ]
  
    MENU_MOVIE_OPT = [Source.MENU_MOVIE_SEARCH,
                     Source.MENU_MOVIE_LAST,
                     #Source.MENU_MOVIE_TOPVIEW,
                     #Source.MENU_MOVIE_TOPWEEK,
                     Source.MENU_MOVIE_TOPRATE
                     #Source.MENU_MOVIE_CATEGORY_ALPHA,
                     #Source.MENU_MOVIE_CATEGORY_GENRE
                     ]    
    
    MENU_MOVIE_HD_OPT = []    
    
    MENU_TVSHOW_OPT = [] 
    
    MENU_ANIME_OPT = [] 
    
    def isLogin(self):          
        return True
    
    def login(self):
        """
            Method to login
        """        
        pass
    
    def removeFilmComplet(self,title):
        """
            Method to remove 'Film Complet en Streaming' on title
            @param title: the name
            
            @return the new title
        """            
        patternXStream = re.compile('(.*)( Film Complet en Streaming)')
        match = patternXStream.match(title.strip())
        if match is not None:           
            newTitle = match.group(1)
        else:
            newTitle = title
        
        return newTitle.strip()
            
    def searchMovie(self, title):
        """
            Method to search a movie
            @return a list of StreamItem
        """
        # Use get ?s=300
        get_href = '?s='+webUtil.encodeStr(title)
        
        response = self.openPage(get_href)
        elementList = []
        
        if response and response.getcode() == 200:    
            content = response.read()
            soup = BeautifulSoup(content)      
                      
            # For every post, get title and topicLink      
            if soup.find('div',{'class':'post-list group'}) is not None:    
                movies = soup.find('div',{'class':'post-list group'}).findAll('article')
            else:
                return elementList
            
            for index in range(0,len(movies)):
                
                movie = movies[index]
                el = movie.find('h2',{'class':'post-title entry-title'}).find('a')
                title = el.text.encode('UTF-8')
                title = strUtil.unescapeHtml(str(title))
                # Remove '  Film Complet en Streaming'
                title = self.removeFilmComplet(title)
                self.__LOGGER__.log("Finded title: "+title,xbmc.LOGDEBUG)
                href = el['href']
                year = strUtil.getYearFromTitle(title) 
                quality = strUtil.getQualityFromTitle(title)  
                lang = strUtil.getLangFromTitle(title)
                title = strUtil.cleanTitle(title)                
                self.__LOGGER__.log("Clean title: "+str(title),xbmc.LOGDEBUG)        
                
                # __ Create the element
                element = StreamItem(title)
                element.setHref(href)                
                element.setYear(year)             
                element.setQuality(quality)             
                element.setLang(lang)
                element.setAction(StreamItem.ACTION_DISPLAY_LINKS)
                element.setType(StreamItem.TYPE_MOVIE)     
                element.setSourceId(self.ID)           
                                
                # __ Add the element to the list
                elementList.append(element)
        
            
            
        # ___ Error during search the movie
        else:
            miscFunctions.displayNotification('Unable to search Movie ' + title)                   
            self.__LOGGER__.log('Connection ERROR : Failed to open page (' + self.buildHref(get_href) + ')', xbmc.LOGERROR)
    
        return elementList
    
    def searchTvShow(self, title):
        """
            Method to search a tv show
            @return a list of StreamItem
        """
        pass
    
    def searchAnime(self, title):
        """
            Method to search a anime
            @return a list of StreamItem
        """
        pass
    
    def getTvShowSeasons(self, tvShowStreamItem):
        """
            Method to get the seasons list of a tv show
            @return a list of StreamItem
        """
        pass    
    
    def getAnimeSeasons(self, tvShowStreamItem):
        """
            Method to get the seasons list of an anime
            @return a list of StreamItem
        """
        pass
    
    def getTvShowEpisodes(self, episodeStreamItem):
        """
            Method to get the episodes list of a season
            @return a list of StreamItem
        """
        pass
    
    def getAnimeEpisodes(self, episodeStreamItem):
        """
            Method to get the episodes list of a season
            @return a list of StreamItem
        """
        pass
    
    def getLinks(self,streamItem):       
        """
            Method to get all links
            @return a list of StreamItem
        """
        # ___ Initialize the list to return
        elementList = []
        
        # ___ Get the soup
        soupI = self._initOpenPage(streamItem)
        
        if soupI is not None:
                    
            divs = soupI.findAll("div",{'class':'video-container'})
            
            
            if divs is not None:   
                for div in divs:       
                    # __ For each iframe
                    iframes = div.findAll("iframe")
                    for iframe in iframes:
                        if (iframe['src'].startswith('http://') or iframe['src'].startswith('https://') or iframe['src'].startswith('//')):
                            
                            # __ Get the link
                            href = iframe['src'].encode('UTF-8')
                            href = self.formatLink(href)
                            # __ Create the element                       
                            element = streamItem.copy()
                            element.setAction(StreamItem.ACTION_PLAY)
                            element.setType(StreamItem.TYPE_STREAMING_LINK)
                            element.setHref(href)                 
                            element.regenerateKodiTitle()
                            
                            self.appendLinkInList(element, elementList)
                    
                    # __ For each embed
                    embeds = div.findAll("embed")
                    for embed in embeds:
                        if (embed['src'].startswith('http://') or embed['src'].startswith('https://') or embed['src'].startswith('//')):
                            # __ Get the link
                            href = embed['src'].encode('UTF-8')
                            href = self.formatLink(href)
                            # __ Create the element                       
                            element = streamItem.copy()
                            element.setAction(StreamItem.ACTION_PLAY)
                            element.setType(StreamItem.TYPE_STREAMING_LINK)
                            element.setHref(href)                        
                            element.regenerateKodiTitle()
                            
                            self.appendLinkInList(element, elementList)                                                             
                          
        return elementList
    
    
    
    def getMovieLink(self,movieStreamItem):
        """
            Method to get all links of a movie
            @return a list of StreamItem
        """
        return self.getLinks(movieStreamItem)
    
    def getTvShowEpisodeLink(self,episodeStreamItem):
        """
            Method to get all links of an episode
            @return a list of StreamItem
        """
        pass    
    
    def getAnimeEpisodeLink(self,episodeStreamItem):
        """
            Method to get all links of an episode
            @return a list of StreamItem
        """
        pass
    
    def getLastMovie(self,streamItem=False):
        """
            Method to get all last movie
            @return a list of StreamItem
        """                
        response = self.openPage('')
        elementList = []
        
        if response and response.getcode() == 200:    
            content = response.read()                    
            soup = BeautifulSoup(content)      
                  
            # For every post, get title and topicLink          
            movies = soup.find('ul',{'id':'tab-recent-2'}).findAll('li')
            
            for index in range(0,len(movies)):
                
                movie = movies[index]
                el = movie.find('p',{'class':'tab-item-title'}).find('a')
                title = el.text.encode('UTF-8')
                title = strUtil.unescapeHtml(str(title))
                # Remove '  Film Complet en Streaming'
                title = self.removeFilmComplet(title)
                self.__LOGGER__.log("Finded title: "+title,xbmc.LOGDEBUG)
                href = el['href']
                year = strUtil.getYearFromTitle(title) 
                quality = strUtil.getQualityFromTitle(title)  
                lang = strUtil.getLangFromTitle(title)
                title = strUtil.cleanTitle(title)                
                self.__LOGGER__.log("Clean title: "+str(title),xbmc.LOGDEBUG)        
                
                # __ Create the element
                element = StreamItem(title)
                element.setHref(href)                
                element.setYear(year)             
                element.setQuality(quality)             
                element.setLang(lang)
                element.setAction(StreamItem.ACTION_DISPLAY_LINKS)
                element.setType(StreamItem.TYPE_MOVIE)                
                                
                # __ Add the element to the list
                elementList.append(element)
        # ___ Error during open last movie page
        else:
            miscFunctions.displayNotification('Unable to get last movie ')                   
            self.__LOGGER__.log('Connection ERROR : Failed to open page (' + self.buildHref('') + ')', xbmc.LOGERROR)
    
        return elementList
    
    def getLastTvShow(self,streamItem=False):
        """
            Method to get all last tv show
            @return a list of StreamItem
        """
        pass
    
    def getLastAnime(self,streamItem=False):
        """
            Method to get all last anime
            @return a list of StreamItem
        """
        pass  
    
    def getTopMovie(self,streamItem=False):
        """
            Method to get top movie
            @return a list of StreamItem
        """
        href=''              
        response = self.openPage(href)
        elementList = []
        
        if response and response.getcode() == 200:    
            content = response.read()                                
            soup = BeautifulSoup(content)      
                  
            # For every post, get title and topicLink          
            movies = soup.find('ul',{'id':'tab-popular-2'}).findAll('li')
            
            for index in range(0,len(movies)):
                
                movie = movies[index]
                el = movie.find('p',{'class':'tab-item-title'}).find('a')
                title = el.text.encode('UTF-8')
                title = strUtil.unescapeHtml(str(title))
                # Remove '  Film Complet en Streaming'
                title = self.removeFilmComplet(title)
                self.__LOGGER__.log("Finded title: "+title,xbmc.LOGDEBUG)
                href = el['href']
                year = strUtil.getYearFromTitle(title) 
                quality = strUtil.getQualityFromTitle(title)  
                lang = strUtil.getLangFromTitle(title)
                title = strUtil.cleanTitle(title)                
                self.__LOGGER__.log("Clean title: "+str(title),xbmc.LOGDEBUG)        
                
                # __ Create the element
                element = StreamItem(title)
                element.setHref(href)                
                element.setYear(year)             
                element.setQuality(quality)             
                element.setLang(lang)
                element.setAction(StreamItem.ACTION_DISPLAY_LINKS)
                element.setType(StreamItem.TYPE_MOVIE)                
                                
                # __ Add the element to the list
                elementList.append(element)          
            
        # ___ Error during open last movie page
        else:
            miscFunctions.displayNotification('Unable to get top movie ')                   
            self.__LOGGER__.log('Connection ERROR : Failed to open page (' + self.buildHref(href) + ')', xbmc.LOGERROR)
    
        return elementList
    
    
    def getTopTvShow(self,streamItem=False):
        """
            Method to get top tv show
            @return a list of StreamItem
        """
        pass
    
    
    def getTopAnime(self,streamItem=False):
        """
            Method to get top anime
            @return a list of StreamItem
        """
        pass
    
    def getMostViewMovie(self,streamItem=False):
        """
            Method to get top week movie
            @return a list of StreamItem
        """
        pass
    
    
    def getMostViewTvShow(self,streamItem=False):
        """
            Method to get top week tv show
            @return a list of StreamItem
        """
        pass
    
    
    def getMostViewAnime(self,streamItem=False):
        """
            Method to get top week anime
            @return a list of StreamItem
        """        
        pass
    
    def getTopWeekMovie(self,streamItem=False):
        """
            Method to get top week movie
            @return a list of StreamItem
        """
        pass
    
    
    def getTopWeekTvShow(self,streamItem=False):
        """
            Method to get top week tv show
            @return a list of StreamItem
        """
        pass
    
    
    def getTopWeekAnime(self,streamItem=False):
        """
            Method to get top week anime
            @return a list of StreamItem
        """
        pass
    
    def getAlphabeticMovieList(self,letter,page):
        
        """
            Method to get an alphabatic list of movie
            @return a list of StreamItem
        """
        pass
    def getAlphabeticTvShowList(self,letter,page):
        
        """
            Method to get an alphabatic list of tv show
            @return a list of StreamItem
        """
        pass
    def getAlphabeticAnimeList(self,letter,page):
        
        """
            Method to get an alphabatic list of anime
            @return a list of StreamItem
        """
        pass
    
    def getStreamingLink(self,href):
        
        """
            Method to get all links in a page
            @return a list of link
        """
        pass
    
    def getSettingsXml(self):
        """
            Method to get the xml settings of the current source
        """
        xmlSettingStr = ''
        xmlSettingStr += '<setting label="Fullmoviz" type="lsep"/>\n'
        xmlSettingStr += '<setting id="src_fullmoviz_activated" type="bool" label="52001" default="true"/>\n'
        return xmlSettingStr