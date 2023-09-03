import sys
sys.path.append('../')

import connector

from microdot_asyncio import Microdot

app = Microdot()

@app.route('/')
async def hello(request):
    return 'Hello, world!'

app.run()