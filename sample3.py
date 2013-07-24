'''
The MIT License (MIT)

Copyright (c) 2013 David Elfi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

################################################################################################
'''
   Equal sequence searcher
'''
def matchingString(s1, s2):
    '''Compare 2 sequence of strings and return the matching sequences concatenated'''
    from difflib import SequenceMatcher
    
    matcher = SequenceMatcher(None, s1, s2)
    output = ""
    for (i,_,n) in matcher.get_matching_blocks():
        output += s1[i:i+n]
    
    return output

################################################################################################
'''
    Run the full sequence
'''
def matchingStringSequence( seq ):
    '''
        Compare between pairs up to final result
    '''
    try:
        matching = seq[0]
        for s in seq[1:len(seq)]:
            matching = matchingString(matching, s)
        
        return matching
    except TypeError:
        return ""

################################################################################################
'''
    Read files content and create sequence
    Input is a sequence of lists with all the instances of same file
    Input = {
        file1: [ <path_to_version_1>, <path_to_version_2>, ... , <path_to_version_n> ],
        file2: ... 
    }
    
    Output = {
        file1: [ <content_version_1>, <content_version_2>, ... , <content_version_n> ],
        file2: ...
    }
'''
def readContent(file_list):
    fullcontent = {}
    
    # Iterate over the list of files
    for i in file_list:
        fullcontent[i] = []
        
        # For each file, read all its content
        for j in file_list[i]:
            f = open(j, 'r')
            fullcontent[i].append(f.read())
            f.close()
            
    return fullcontent

###############################################################################

if __name__ == '__main__':
    import urllib2, sys, os
    
    # URL
    url_str = sys.argv[1]
    
    # Check folder is available
    foldername = urllib2.quote(url_str)
    foldername = foldername.replace("/", "-")
    tmp_folder = os.sep + "tmp" + os.sep + foldername 
    if not os.path.exists(tmp_folder):
        print "Folder '%s' does not exist. Check URL" % tmp_folder
        exit(1)
    
    # Build file lists
    tempdir_list = os.listdir(tmp_folder)
    fulldir_list = {}
    
    # Read parent folder list
    for f in tempdir_list:
        temp_folder_list = os.listdir(tmp_folder + os.sep + f)
        
        # Add files to the full list of files to be analyzed
        for innerf in temp_folder_list:
            try:
                fulldir_list[innerf].append(tmp_folder + os.sep + f + os.sep + innerf)
            except:
                fulldir_list[innerf] = [ tmp_folder + os.sep + f + os.sep + innerf, ]

    text_compare = readContent(fulldir_list)
    
    # Let's analyze each file
    for i in text_compare:
        print "Comparing %s..." % i
        
        # Debug... just for the sake of presentation
        if '-' == i:
            temp_str = matchingStringSequence(text_compare[i])
            print "Areas to cache:\n%s" % temp_str