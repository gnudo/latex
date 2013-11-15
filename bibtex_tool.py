'''
Created on Nov 12, 2013

@author: Goran Lovric
@summary: Tools for extracting chosen references from bibtex-files
'''
import re
import sys

class BIB_File(object):
    '''
    Class of a bibtex-file containing references
    '''
    def __init__(self,ref_file):
        self.ref_file = open(ref_file)
        self.lines = self.ref_file.readlines()
        self.refs = []
        self.ref_line_start = []
        self.ref_line_end = []
        
        ''' Get refs and line numbers'''
        self.get_refs_list()
        self.fill_ending_line()       
        
    def get_refs_list(self):
        '''
        Extracts all refs with respective (beginning) line numbers
        '''
        searchpat = re.compile("\@(.*)\{")
        for kk,lines in enumerate(self.lines):
            if re.match(searchpat,lines):
                tmp = re.split(searchpat,lines)[2]
                self.refs.append(tmp[:-2])
                self.ref_line_start.append(kk)

    def fill_ending_line(self):
        '''
        Fill list "ref_line_end" with ending line number for each reference.
        '''
        if len(self.ref_line_start) == 0:
            sys.exit('The method get_refs_list has to be run first!')
        for nr in self.ref_line_start:
            brackets_order = 1
            line_nr = 1
            while brackets_order != 0:
                search1 = re.compile("(.*)\{(.*)")
                search2 = re.compile("(.*)\}(.*)")
                tmp_line = self.lines[nr+line_nr]
                if re.match(search1,tmp_line):
                    brackets_order = brackets_order+1
                if re.match(search2,tmp_line):
                    brackets_order = brackets_order-1
                line_nr = line_nr + 1
            self.ref_line_end.append(line_nr+nr)
        
        if len(self.ref_line_start) != len(self.ref_line_end):
            sys.exit('Something is wrong with parsing brackets in bib-file - probably DEBUG more...')         
        

class BBL_File(object):
    '''
    Class of a bbl-file that is used as input for extracting references from
    the bibtex file
    '''
    def __init__(self,bbl_file):
        self.bbl_file = open(bbl_file)
        self.lines = self.bbl_file.readlines()
        self.refs = []
        
        self.get_refs_list()
    
    def get_refs_list(self):
        '''
        Extracts all refs from a bbl-file
        '''
        bibitem = re.compile("(.*)bibitem(.*)")
        for lines in self.lines:
            if re.match(bibitem,lines):
                reference = lines[lines.find("bibitem{")+8:lines.find("}")]
                self.refs.append(reference)

class New_refs(object):
    '''
    Class for creating 1 single bib-file by extracting references
    from different bib-files.
    '''   
    def __init__(self,bib_files):
        self.bib_files = []
        if isinstance(bib_files, basestring):
            self.bib_files.append(BIB_File(bib_files))
        else:
            for bib in bib_files:
                self.bib_files.append(BIB_File(bib))
    
    def find_corresponding_bibs(self,bbl_file):
        ''' Finds which refs have to be extracted from which bib file'''
        bbl_file = BBL_File(bbl_file)
        self.bbl_lists=[]
        for ii in range(len(self.bib_files)):
            tmp_set = set(bbl_file.refs).intersection( set(self.bib_files[ii].refs) )
            self.bbl_lists.append(list(tmp_set))
    
    def extract_refs(self,num):
        ref_list = self.bbl_lists[num]
        bib = self.bib_files[num].refs
        '''extract refs from bib file and add to file'''
        tmp_matches =  [j for i in range(len(ref_list)) for j in range(len(bib)) if ref_list[i] == bib[j]]
        with open(self.newfile, "a") as myfile:
            for ii in tmp_matches:
                start = self.bib_files[num].ref_line_start[ii]
                end = self.bib_files[num].ref_line_end[ii]
                for jj in range(start, end):
                    myfile.write(self.bib_files[num].lines[jj])
    
    def extract_all_refs(self):
        '''extract all refs from all bib files'''
        for ii in range(len(self.bib_files)):
            self.extract_refs(ii)
    
    def create_new_bibfile(self, bbl_file, newfile):
        self.newfile = newfile
        open(self.newfile,"w").close()
        
        self.find_corresponding_bibs(bbl_file)
        self.extract_all_refs()


if __name__ == "__main__":
    bib_file1 = "/afs/psi.ch/user/l/lovric_g/Documents/latex/bibtex/library.bib"
    bib_file2 = "/afs/psi.ch/user/l/lovric_g/Documents/latex/bibtex/books.bib"
    bbl_file = "/afs/psi.ch/user/l/lovric_g/Documents/papers/coherence/lovric_talbot_v1.bbl"
    
    aa = New_refs([bib_file1,bib_file2])
    aa.create_new_bibfile(bbl_file, "/afs/psi.ch/user/l/lovric_g/Desktop/library.bib")

