import sys
sys.path.append('../')

from microdot import Microdot, send_file
import connector

app = Microdot()

@app.route('/')
def hello(request):
    return send_file('hello.html')


@app.route('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'


app.run()
