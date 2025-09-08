import logging
import os
import time

from config import NODE_IDENTITY_PATH, RNS_CONFIGDIR, ANNOUNCE_NAME
from modules.html2mu.html2mu import convert_html_to_markdown, webpage_to_micron
from modules.nomadapi import NomadAPI
from modules.nomadapi.app import Config, create_rns_dest
from modules.nomadapi.handlers import Request, render_template

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

def log_usage(id, url, t0):
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
    print(f"{formatted_time}: {id=} {url=}, {time.time() - t0:.2f}s")

    log_file = 'usage_log.csv'
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write('timestamp,identity,url,duration\n')

    with open(log_file, 'a') as f:
        f.write(f'"{formatted_time}","{id}","{url}",{time.time() - t0:.2f}\n')


@app.request('/page/web.mu')
def web(r: Request):
    if r.has_param('url'):
        id = r.get_remote_identity() if r.remote_identity else None
        url = r.get_param('url')
        if url.startswith('http://') or url.startswith('https://'):
            pass
        else:
            url = 'https://' + url  # default to https

        t0 = time.time()
        mu = webpage_to_micron(url)

        log_usage(id, url, t0)
        return mu
    else:
        return 'no url provided'

@app.request('/page/browser.mu')
def browser(r: Request):
    return render_template('browser.mu', dict())

if __name__ == '__main__':
    dst, identity = create_rns_dest(RNS_CONFIGDIR, NODE_IDENTITY_PATH)

    app.scheduler.every(10).minutes.do(
        lambda: logging.getLogger("announce").debug(
            "announce with data %s", ANNOUNCE_NAME
        )
        or dst.announce(ANNOUNCE_NAME.encode("utf-8"))
    )

    app.register_handlers(dst)
    app.run()
