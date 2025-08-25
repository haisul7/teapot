import logging

from config import NODE_IDENTITY_PATH, RNS_CONFIGDIR, ANNOUNCE_NAME
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


if __name__ == '__main__':
    dst, identity = create_rns_dest(RNS_CONFIGDIR, NODE_IDENTITY_PATH)

    app.scheduler.every(5).minutes.do(
        lambda: logging.getLogger("announce").debug(
            "announce with data %s", ANNOUNCE_NAME
        )
        or dst.announce(ANNOUNCE_NAME.encode("utf-8"))
    )

    app.register_handlers(dst)
    app.run()
