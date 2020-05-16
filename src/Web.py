from microWebSrv import MicroWebSrv
import ujson

_ledController = None
_scheduler = None

class Web:
 
    def __init__(self, ledController, scheduler):
        global _ledController
        global _scheduler
        _ledController = ledController
        _scheduler = scheduler

@MicroWebSrv.route('/state', 'GET')
def httpHandlerStateGet(httpClient, httpResponse):
    global _scheduler

    content = _scheduler.to_json()

    httpResponse.WriteResponseOk(   headers         = None,
                                    contentType     = "application/json",
                                    contentCharset  = "UTF-8",
                                    content         = content)


@MicroWebSrv.route('/state/mode', 'PUT')
def httpHandlerModePut(httpClient, httpResponse):
    global _scheduler

    new_mode = httpClient.ReadRequestContent().decode('utf-8')
    print(new_mode)
    _scheduler.set_mode(new_mode)
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content="")

@MicroWebSrv.route('/state/staticcolour', 'PUT')
def httpHandlerStaticColourPut(httpClient, httpResponse):
    global _scheduler
    colour_json = httpClient.ReadRequestContent().decode('utf-8')
    colour = ujson.loads(colour_json)
    _scheduler.set_static_colour(colour.get("r", 0), colour.get("g", 0), colour.get("b", 0), colour.get("w", 0))
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content="")

@MicroWebSrv.route('/state/triggersavecurrentconfig', 'POST')
def httpHandlerSaveCurrentConfigPost(httpClient, httpResponse):
    global _scheduler
    _scheduler.save_scheduler_config()
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content="")

@MicroWebSrv.route('/state/rainbowsettings', 'PUT')
def httpHandlerRainbowSettingsPut(httpClient, httpResponse):
    global _scheduler
    rainbow_json = httpClient.ReadRequestContent().decode('utf-8')
    rainbow = ujson.loads(rainbow_json)
    _scheduler.set_rainbow_brightness(rainbow.get("brightness", 16))
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content="")

@MicroWebSrv.route('/state/schedule/<hour>/<minute>', 'PUT')
def httpHandlerSchedulePut(httpClient, httpResponse, routeArgs):
    global _scheduler
    colour_json = httpClient.ReadRequestContent().decode('utf-8')
    colour = ujson.loads(colour_json)
    _scheduler.add_schedule_item(colour.get("r", 0), colour.get("g", 0), colour.get("b", 0), colour.get("w", 0), routeArgs["hour"], routeArgs["minute"])
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content="")

@MicroWebSrv.route('/state/schedule/<hour>/<minute>', 'DELETE')
def httpHandlerScheduleDelete(httpClient, httpResponse, routeArgs):
    global _scheduler
    _scheduler.delete_schedule_item(routeArgs["hour"], routeArgs["minute"])
    httpResponse.WriteResponseOk(headers=None, contentType="text/html", contentCharset="UTF-8", content="")

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
