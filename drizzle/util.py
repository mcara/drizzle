from __future__ import division, print_function, unicode_literals, absolute_import

# SYSTEM
import os
import os.path

# THIRD-PARTY
import numpy as np
from astropy.io import fits

def find_keyword_extn(fimg, keyword, value=None):
    """
    This function will return the index of the extension in a multi-extension
    FITS file which contains the desired keyword with the given value.
    """

    i = 0
    extnum = -1
    # Search through all the extensions in the FITS object
    for chip in fimg:
        hdr = chip.header
        # Check to make sure the extension has the given keyword
        if keyword in hdr:
            if value is not None:
                # If it does, then does the value match the desired value
                # MUST use 'str.strip' to match against any input string!
                if hdr[keyword].strip() == value:
                    extnum = i
                    break
            else:
                extnum = i
                break
        i += 1
    # Return the index of the extension which contained the
    # desired EXTNAME value.
    return extnum

def get_extn(fimg, extn=''):
    """
    Returns the FITS extension corresponding to extension specified in
    filename. Defaults to returning the first extension with data or the 
    primary extension, if none have data.
    """

    if extn:
        try:
            _extn = parse_extn(extn)
            _e = fimg.index_of(extn)
        except KeyError:
            _e = None

        if _e is None:
            _extn = None
        else:
            _extn = fimg[_e]

    else:
        # If no extension is provided, search for first extension
        # in FITS file with data associated with it.

        # Set up default to point to PRIMARY extension.
        _extn = fimg[0]
        # then look for first extension with data.
        for _e in fimg:
            if _e.data is not None:
                _extn = _e
                break

    return _extn    

def get_keyword(filename, keyword, default=None):
    """
    General, write-safe method for returning a keyword value from the header of
    an image.
    """

    value = None
    if keyword:
        # Insure that there is at least 1 extension specified...
        if filename.find('[') < 0:
            filename += '[0]'
    
        _fname, _extn = parse_filename(filename)
        _fimg = fits.open(_fname)
    
        # Address the correct header
        _extn = get_extn(_fimg, _extn)
    
        if _extn is not None:
            _hdr = _extn.header
            try:
                value =  _hdr[keyword]
            except KeyError:
                _nextn = find_keyword_extn(_fimg, keyword)
                try:
                    value = _fimg[_nextn].header[keyword]
                except KeyError:
                    value = None
        
        _fimg.close()
        del _fimg

    if value is None and default is not None:
        value = default

    return value

def is_blank(val):
    """
    Determines whether or not a value is considered 'blank'.
    """
    return val.strip() == ""

def parse_extn(extn=''):
    """
    Parse a string representing a qualified fits extension name as in the
    output of parse_filename and return a tuple (str(extname), int(extver)),
    which can be passed to pyfits functions using the 'ext' kw.
    Default return is the first extension in a fits file.

    Examples
    --------
        >>>parse_extn('sci,2')
        ('sci', 2)
        >>>parse_extn('2')
        ('', 2)
        >>>parse_extn('sci')
        ('sci', 1)
    """
    if not extn:
        return ('', 0)

    try:
        lext = extn.split(',')
    except:
        return ('', 1)

    if len(lext) == 1 and lext[0].isdigit():
        return ("", int(lext[0]))
    elif len(lext) == 2:
        return (lext[0], int(lext[1]))
    else:
        return (lext[0], 1)

def parse_filename(filename):
    """
    Parse out filename from any specified extensions.
    Returns rootname and string version of extension name.
    """
    # Parse out any extension specified in filename
    _indx = filename.find('[')
    if _indx > 0:
        # Read extension name provided
        _fname = filename[:_indx]
        _extn = filename[_indx+1:-1]
    else:
        _fname = filename
        _extn = ''

    return _fname, _extn

def set_orient(the_wcs):
    """
    Computes ORIENTAT from the CD matrix
    """
    cd12 = the_wcs.wcs.cd[0][1]
    cd22 = the_wcs.wcs.cd[1][1]
    the_wcs.orientat = np.rad2deg(np.arctan2(cd12,cd22))

def set_pscale(the_wcs):
    """
    Calculates the plate scale from the CD matrix
    """
    cd11 = the_wcs.wcs.cd[0][0]
    cd21 = the_wcs.wcs.cd[1][0]
    the_wcs.pscale = np.sqrt(np.power(cd11,2)+np.power(cd21,2)) * 3600.