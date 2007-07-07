#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# Authors :
#	Ouattara Oumar Aziz ( alias wattazoum ) <wattazoum@gmail.com>

from exceptions import *
import os

class SBdict (dict) :
	"""
	This is a structure used by sbackup to store flist and fprops . 
	The structure is in fact a tree meant to :
	- ease the retrieval of the content of a folder
	- to optimise the use of memory to store the flist file by avoiding to store identical subpath.
	
	The flist file has this contents :
	
	/home
	/home/wattazoum
	/home/wattazoum/Desktop
	/home/wattazoum/Desktop/sbackup-test
	/home/wattazoum/Desktop/sbackup-test/d17
	/home/wattazoum/Desktop/sbackup-test/d17/d3
	/home/wattazoum/Desktop/sbackup-test/d17/d3/f4.txt
	/home/wattazoum/Desktop/sbackup-test/d17/d2
	/home/user/Desktop/sbackup-test/d17/d3/f4.txt
	
	The goal of SBdict is to store the data this way
	
	/home	->wattazoum	->Desktop	->sbackup-test	->d17	->d3	->f4.txt
															->d2
			->user		->Desktop	->sbackup-test	->d17	->d3	->f4.txt
	
	We use for that this node :
	{ 'file' : [ 'props', sonNode ] }
	
	Example : 
	 
	{ 'home' : [ 'props', {
		 'wattazoum' : [ 'props', { 
		 	'Desktop' : [ 'props', { 
		 		'sbackup-test' : [ 'props', { 
		 			'd17' : [ 'props', { 
		 				'd3' : [ 'props', { 
		 					'f4.txt' : [ 'props', None ] } ] ,
		 				'd2' : [ 'props', None ] } ] } ] } ] } ] , 
		 'user' : [ 'props', { 
		 	'Desktop' : [ 'props', {
		 		'sbackup-test' : [ 'props', { 
		 			'd17' : [ 'props', { 
		 				'd3' : [ 'props', { 
		 					'f4.txt' : [ 'props', None ] } ] } ] } ] } ] } ] 
		 } ] } 
	
	We can save the memory for all subpathes but then, we might have a lost of speed when doing some search
	( comparing to putting the whole file in a Dictionary )
	"""
	def __init__(self, mapping=None):
		if not mapping :
			dict.__init__(self)
		else :
			if type(mapping) == list and type(mapping[0]) ==tuple and len(mapping[0]) == 2 :
				dict.__init__(self)
				for key,value in mapping :
					self.__setitem__(key, value)
			else :
				raise Exception ("Not implemented yet")
	
	def getSon(self, path) :
		"""
		get the son SBdict of a path
		@param path: the path to get the son of
		@return: a SBdict or None if there were no son
		"""
		if self.has_key(path) :
			return self[path][1]
		else :
			raise SBException("'%s' not in SBdict"% path)
		
	def setSon(self,path, son):
		"""
		Set the son of a path 
		(/!\ the props of the path will be set to None if the key didn't exist )
		@param path: the path to set the son on
		@param son: the son as a SBdict  
		"""
		if son != None and type(son) != SBdict :
			raise CorruptedSBdictException("You can't set '%s' as a son " % str(son))
		if not self[path] or self[path][0] == None :
			self.__setitem(path,[None,son])
		else :
			self.__setitem__(path,[self[path][0],son])
		
	def has_key(self, key) :
		"""
		Return True if the path have been found and false if not
		@param key: a path to search (/home/user/test/dir )
		"""

		splited = key.split(os.sep,1)
		
		if not dict.has_key(self,splited[0]) :
			return False
		else : # base dir found, we look for the son
			# if the son is empty, we found our element
			if len(splited) == 1 or not splited[1] :
				return True
			if self[splited[0]][1] != None :
				if type(self[splited[0]][1]) == SBdict :
					return self[splited[0]][1].has_key(splited[1])
				else :
					raise CorruptedSBdictException("The value stored in the SBdict is Invalid : " + str(type(self[splited[0]][1])))
			else : return False
	
	def __setitem__(self, key, value ) :
		"""
		Add an item
		@param key: a string 
		@param value: Value must be None , a String or a 2 length list with None or an SBdict on the second member
		@raise CorruptedSBdictException: 
		"""
		valIsStr = False
		
		if value != None :
			if type(value) == str :
				valIsStr = True
			elif (type(value) != list or len(value) != 2 or (value[1] != None and (type(value[1]) != SBdict or value[1] == SBdict() )) ):
				raise CorruptedSBdictException(" '%s' is not a valid value for an SBdic " % value)
		
		splited = key.split(os.sep,1)
		
		if len(splited) == 1 or not splited[1] :
			# we are at the end of a path 
			# we fallback to the normal behaviour
			if dict.has_key(self,splited[0]) :
				# The key exists
				item = dict.__getitem__(self,splited[0])
				if valIsStr : prop = value
				else : prop = value[0]
				if valIsStr :
					dict.__setitem__(self,splited[0],[prop,item[1]])
				else :
					if value[1] == None :	
						dict.__setitem__(self,splited[0],[prop,item[1]])
					else :
						dict.__setitem__(self,splited[0],value)
			else :
				#the key doesn't exist
				if valIsStr : dict.__setitem__(self,splited[0],[value,None])
				else : dict.__setitem__(self,splited[0],value)
		else : # path is composed , 
			# we check if the base dir exists and get the props infos
			if dict.has_key(self,splited[0]) :
				item = dict.__getitem__(self,splited[0])
				prop = item[0]
				if item[1] != None :
					if type(item[1]) != SBdict : 
						raise CorruptedSBdictException("The value stored in the SBdict is Invalid : " + str(item[1])) 
					son = item[1]
				else :
					son = SBdict()
			else:
				prop = None
				son = SBdict()
			son.__setitem__(splited[1], value)
			dict.__setitem__(self, splited[0],[prop,son])
			
	def __getitem__(self,key) :
		"""
		Return the item Value
		@param key: a path to search (/home/user/test/dir )
		@return: False if the item is not found
		"""
		splited = key.split(os.sep,1)
		
		if not dict.has_key(self,splited[0]) :
			return False
		else : # base dir found, we look for the son
			# if the son is empty, we found our element
			if len(splited) == 1 or not splited[1] :
				return dict.__getitem__(self,splited[0])
			if self[splited[0]][1] != None :
				if type(self[splited[0]][1]) == SBdict :
					return self[splited[0]][1].__getitem__(splited[1])
				else :
					raise CorruptedSBdictException("The value stored in the SBdict is Invalid : " + str(type(self[splited[0]][1])))
			else : return False
		
	def iterkeys(self,_path=None) :
		"""
		an Iterator that gets recursively the full path
		Should return fullpath
		"""
		if _path is None: # initialization
			_path = []
		for dirname,(props, son) in dict.iteritems(self):
			_path.append(dirname)
			yield os.sep.join(_path)
			if son is None:
				_path.pop()
			else:
				for path in son.iterkeys(_path):
					yield path
		if len(_path) > 0 :
			_path.pop()
	
	def iteritems(self,_path=None) :
		"""
		an Iterator that gets recursively the full path with its properties
		Should return (fullpath, props)
		"""
		if _path is None: # initialization
			_path = []
		for dirname,(props, son) in dict.iteritems(self):
			_path.append(dirname)
			yield (os.sep.join(_path), props) 
			if son is None:
				_path.pop()
			else:
				for path, prop in son.iteritems(_path):
					yield (path, prop )
		if len(_path) > 0 :
			_path.pop()
		
	def itervalues(self,_path=None) :
		"""
		an Iterator that gets recursively the full path
		Should return props
		"""
		if _path is None: # initialization
			_path = []
		for dirname,(props, son) in dict.iteritems(self):
			_path.append(dirname)
			yield props
			if son is None:
				_path.pop()
			else:
				for prop in son.itervalues(_path):
					yield prop
		if len(_path) > 0 :
			_path.pop()