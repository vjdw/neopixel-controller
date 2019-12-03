from microWebSrv import MicroWebSrv

_ledController = None

class Web:
 
    def __init__(self, ledController):
        global _ledController
        _ledController = ledController

@MicroWebSrv.route('/test')
def httpHandlerTestGet(httpClient, httpResponse):
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
            <form action="/test" method="post" accept-charset="ISO-8859-1">
                R: <input type="number" name="R"><br />
                G: <input type="number" name="G"><br />
                B: <input type="number" name="B"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """ % httpClient.GetIPAddr()
    httpResponse.WriteResponseOk(   headers		 = None,
                                    contentType	 = "text/html",
                                    contentCharset = "UTF-8",
                                    content 		 = content)

@MicroWebSrv.route('/test', 'POST')
def httpHandlerTestPost(httpClient, httpResponse):
    global _ledController

    formData = httpClient.ReadRequestPostedFormData()

    _ledController.fade_to_colour(int(formData["R"]), int(formData["G"]), int(formData["B"]))

    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            <form action="/test" method="post" accept-charset="ISO-8859-1">
                R: <input type="number" name="R"><br />
                G: <input type="number" name="G"><br />
                B: <input type="number" name="B"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content=content)

mws = MicroWebSrv(webPath="/www")
mws.Start(threaded=True)
