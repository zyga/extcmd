import doctest

def test_suite():
    print "I was called"
    return doctest.DocFileSuite("README")
