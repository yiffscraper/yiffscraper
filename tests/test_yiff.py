import yiff

projid = "7330723"
projname = "Belle Delphine"
projpatreonurl = "https://www.patreon.com/belledelphine"
projyiffurl = "http://yiff.party/patreon/7330723"


# TODO: Find a way to mock out the downloads, so running these tests don't take forever
# def test_scrapeFromPatreonId():
#     yiff.scrape(projid)
#     # TODO: Check result


# def test_scrapeFromPatreonUrl():
#     yiff.scrape(projpatreonurl)
#     # TODO: Check result


# def test_scrapeFromYiffUrl():
#     yiff.scrape(projyiffurl)
#     # TODO: Check result


def test_initSession():
    s = yiff.initSession()
    assert s.cookies.get("party", domain="yiff.party") is not None


def test_getProjectFromPatreonId():
    info = yiff.getProject(projid)
    assert info.id == projid
    assert info.name == projname
    assert info.patreonurl == projpatreonurl
    assert info.yiffurl == projyiffurl


def test_getProjectFromPatronUrl():
    info = yiff.getProject(projpatreonurl)
    assert info.id == projid
    assert info.name == projname
    assert info.patreonurl == projpatreonurl
    assert info.yiffurl == projyiffurl


def test_getProjectFromYiffUrl():
    info = yiff.getProject(projyiffurl)
    assert info.id == projid
    assert info.name == projname
    assert info.patreonurl == projpatreonurl
    assert info.yiffurl == projyiffurl
