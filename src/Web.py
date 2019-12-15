from microWebSrv import MicroWebSrv

_ledController = None
_scheduler = None

class Web:
 
    def __init__(self, ledController, scheduler):
        global _ledController
        global _scheduler
        _ledController = ledController
        _scheduler = scheduler

@MicroWebSrv.route('/test')
def httpHandlerTestGet(httpClient, httpResponse):
    global _scheduler

    scheduleItems = ""
    for schedule_item in _scheduler.schedule:
        scheduleItems = scheduleItems + "<div>{0}</div>".format(schedule_item.to_string())

    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>backlight</title>
        </head>
        <body>
            Client IP address = %s
            <br />
            %s
            <form action="/test" method="post" accept-charset="ISO-8859-1">
                R: <input type="number" name="R" min="0" max="255" value="0"><br />
                G: <input type="number" name="G" min="0" max="255" value="0"><br />
                B: <input type="number" name="B" min="0" max="255" value="0"><br />
                W: <input type="number" name="W" min="0" max="255" value="0"><br />
                <input type="submit" value="Submit">
            </form>

            <form action="/newschedule" method="post" accept-charset="ISO-8859-1">
                R: <input type="number" name="R" min="0" max="255" value="0"><br />
                G: <input type="number" name="G" min="0" max="255" value="0"><br />
                B: <input type="number" name="B" min="0" max="255" value="0"><br />
                W: <input type="number" name="W" min="0" max="255" value="0"><br />
                Hr: <input type="number" name="Hour" min="0" max="23" value="0"><br />
                Min: <input type="number" name="Minute" min="0" max="59" value="0"><br />
                <input type="submit" value="Submit">
            </form>

        </body>
    </html>
    """ % (httpClient.GetIPAddr(), scheduleItems)
    httpResponse.WriteResponseOk(   headers		 = None,
                                    contentType	 = "text/html",
                                    contentCharset = "UTF-8",
                                    content 		 = content)

@MicroWebSrv.route('/test', 'POST')
def httpHandlerTestPost(httpClient, httpResponse):
    global _ledController

    formData = httpClient.ReadRequestPostedFormData()

    _ledController.fade_to_colour(int(formData["R"]), int(formData["G"]), int(formData["B"]), int(formData["W"]))

    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>backlight</title>
        </head>
        <body>
            <form action="/test" method="post" accept-charset="ISO-8859-1">
                R: <input type="number" name="R" min="0" max="255" value="%s"><br />
                G: <input type="number" name="G" min="0" max="255" value="%s"><br />
                B: <input type="number" name="B" min="0" max="255" value="%s"><br />
                W: <input type="number" name="W" min="0" max="255" value="%s"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """ % (formData["R"], formData["G"], formData["B"], formData["W"])
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content=content)

@MicroWebSrv.route('/newschedule', 'POST')
def httpHandlerTestPost(httpClient, httpResponse):
    global _scheduler

    formData = httpClient.ReadRequestPostedFormData()

    _scheduler.add_schedule_item(int(formData["R"]), int(formData["G"]), int(formData["B"]), int(formData["W"]), int(formData["Hour"]), int(formData["Minute"]))

    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>backlight</title>
        </head>
        <body>
            <form action="/newschedule" method="post" accept-charset="ISO-8859-1">
                R: <input type="number" name="R" min="0" max="255" value="%s"><br />
                G: <input type="number" name="G" min="0" max="255" value="%s"><br />
                B: <input type="number" name="B" min="0" max="255" value="%s"><br />
                W: <input type="number" name="W" min="0" max="255" value="%s"><br />
                Hr: <input type="number" name="Hour" min="0" max="23" value="%s"><br />
                Min: <input type="number" name="Minute" min="0" max="59" value="%s"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """ % (formData["R"], formData["G"], formData["B"], formData["W"], formData["Hour"], formData["Minute"])
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content=content)

mws = MicroWebSrv(webPath="/www")
mws.Start(threaded=True)
