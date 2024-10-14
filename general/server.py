import json
from general.llm import GeneralLLM
from sanic import Sanic
from sanic import Request, Websocket
from sanic.response import text
from sanic.worker.manager import WorkerManager

WorkerManager.THRESHOLD = 3000 # 5 minute startup timeout

app = Sanic("general")
app.config.OAS = False # No need for OpenAPI, theoretically creates attack surface

# Run only once, before any workers start to avoid timeouts
@app.before_server_start
async def setup(app, loop):
    app.ctx.llm = GeneralLLM()
    app.ctx.vote_log = open("votes.txt", "a")

@app.after_server_stop
async def teardown(app, loop):
    app.ctx.vote_log.close()

@app.websocket("/chat")
async def chat(request: Request, ws: Websocket):
    #session_id = app.ctx.llm.init_chat()
    async for msg in ws:
        work = json.loads(msg)
        if work["type"] == "init":
            session_id = app.ctx.llm.init_chat()
            await ws.send(json.dumps({'session_id': session_id}))
            print(f"Initiated session {session_id}")
        elif work["type"] == "message":
            human = work["message"]
            session_id = work["session_id"]
            await ws.send(json.dumps({'loading': True}))
            resp = await app.ctx.llm.invoke(human, session_id)
            await ws.send(json.dumps({'message': resp[0], 'sources': list(resp[1])}))
            print(f"Session: {session_id}\nHuman: {human}\nAI: {resp}")
        elif work["type"] == "vote":
            app.ctx.vote_log.write("Vote from session "+str(work["session_id"])+":\r\n")
            app.ctx.vote_log.write("Positive: "+str(work["vote"])+"\r\n")
            app.ctx.vote_log.write(str(work["context"])+"\r\n\r")
            app.ctx.vote_log.flush()
            print("Logged vote "+str(work["vote"])+" from session "+str(work["session_id"]))
        else:
            print("Unknown message: "+str(work))

@app.get("/")
async def hello_world(request):
    return text("Hello, world.")

#if __name__ == "__main__":
#    global llm
#    llm = GeneralLLM()
#    app.run(port=1831)