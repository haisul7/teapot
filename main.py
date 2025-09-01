import logging

from config import NODE_IDENTITY_PATH, RNS_CONFIGDIR, ANNOUNCE_NAME
from src.html2mu.html2mu import convert_html_to_markdown, webpage_to_micron
from src.nomadapi import NomadAPI
from src.nomadapi.app import Config, create_rns_dest
from src.nomadapi.handlers import Request, render_template

app = NomadAPI(
    Config(
        templates_dir='pages'
    )
)

@app.request('/page/index.mu')
def index(r: Request):
    return render_template('index.mu', dict())

@app.request('/page/links.mu')
def links(r: Request):
    return render_template('links.mu', dict())

@app.request('/page/web.mu')
def web(r: Request):
    if r.has_param('url'):
        print(f"{r.get_param('url')=} requested")

        return webpage_to_micron(r.get_param('url'))
    else:
        return 'no url provided'

if __name__ == '__main__':
    dst, identity = create_rns_dest(RNS_CONFIGDIR, NODE_IDENTITY_PATH)

    app.scheduler.every(1).minutes.do(
        lambda: logging.getLogger("announce").debug(
            "announce with data %s", ANNOUNCE_NAME
        )
        or dst.announce(ANNOUNCE_NAME.encode("utf-8"))
    )

    app.register_handlers(dst)
    app.run()
