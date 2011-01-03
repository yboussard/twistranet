
def truncate(text, length, ellipsis=u'\u2026'):
    if text is None:
        text = ''
    if not isinstance(text, basestring):
        raise ValueError("%r is no instance of basestring or None" % text)

    # thread other whitespaces as word break
    content = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    # make sure to have at least one space for finding spaces later on
    content += ' '

    if len(content) > length:
        # find the next space after max_len chars (do not break inside a word)
        pos = length + content[length:].find(' ')
        if pos != (len(content) - 1):
            # if the found whitespace is not the last one add an ellipsis
            text = text[:pos].strip() + ' ' + ellipsis

    return text

def formatbytes(sizeint, configdict=None, **configs):
    """
    Given a file size as an integer, return a nicely formatted string that
    represents the size. Has various options to control it's output.
    
    """
    defaultconfigs = {  'forcekb' : False,
                        'largestonly' : True,
                        'kiloname' : 'KB',
                        'meganame' : 'MB',
                        'bytename' : 'bytes',
                        'nospace' : True}
    if configdict is None:
        configdict = {}
    for entry in configs:
        # keyword parameters override the dictionary passed in
        configdict[entry] = configs[entry]
    #
    for keyword in defaultconfigs:
        if not configdict.has_key(keyword):
            configdict[keyword] = defaultconfigs[keyword]
    #
    if configdict['nospace']:
        space = ''
    else:
        space = ' '
    #
    mb, kb, rb = bytedivider(sizeint)
    if configdict['largestonly']:
        if mb and not configdict['forcekb']:
            return stringround(mb, kb)+ space + configdict['meganame']
        elif kb or configdict['forcekb']:
            if mb and configdict['forcekb']:
                kb += 1024*mb
            return stringround(kb, rb) + space+ configdict['kiloname']
        else:
            return str(rb) + space + configdict['bytename']
    else:
        outstr = ''
        if mb and not configdict['forcekb']:
            outstr = str(mb) + space + configdict['meganame'] +', '
        if kb or configdict['forcekb'] or mb:
            if configdict['forcekb']:
                kb += 1024*mb
            outstr += str(kb) + space + configdict['kiloname'] +', '
        return outstr + str(rb) + space + configdict['bytename']

def bytedivider(nbytes):
    """
    Given an integer (probably a long integer returned by os.getsize() )
    it returns a tuple of (megabytes, kilobytes, bytes).
    
    This can be more easily converted into a formatted string to display the
    size of the file.
    """
    mb, remainder = divmod(nbytes, 1048576)
    kb, rb = divmod(remainder, 1024)
    return (mb, kb, rb)

def stringround(main, rest):
    """
    Given a file size in either (mb, kb) or (kb, bytes) - round it
    appropriately.
    """
    # divide an int by a float... get a float
    value = main + rest/1024.0
    return str(round(value, 1))
