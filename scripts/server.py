#!/usr/bin/env python

from bottle import route, run, template, static_file, request
from collections import defaultdict
import os
from os import walk
import subprocess
import hashlib
import json

#_root_folder = 'S:\\300\\320\\327\\'
_root_folder = '.'
_cache = '_cache.json'

_files = None
_checksum = None

def gethtml(title, content):
    ans = '<html> \
            <head>' +\
              '<title>{}</title>'.format(title) +\
              '<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\
              <!-- jQuery (necessary for Bootstraps JavaScript plugins) --> \
              <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script> \
              <!-- Include all compiled plugins (below), or include individual files as needed --> \
              <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>'
    ans += '<meta name="viewport" content="width=device-width, initial-scale=1">'
    ans +=  '</head>' + \
            '<body>' + \
            '{}'.format(content) + \
            '</body>' + \
        '</html>'
    return ans

def gethtml_bs(title, content, refresh_time_s=None, redirect_url=None):
    ans = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
'''
    ans += '<title>{}</title>'.format(title)
    if refresh_time_s is not None:
        refresh_meta = '<meta http-equiv="Refresh" content="{};'.format(refresh_time_s)
        if redirect_url is not None:
            refresh_meta += 'url={}" />'.format("'{}'".format(redirect_url))
        else:
            refresh_meta += '"/>'
        ans += refresh_meta
    ans +='''
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js" integrity="sha384-cVKIPhGWiC2Al4u+LWgxfKTRIcfu0JTxR+EQDz/bgldoEyl4H0zUF0QKbrJ0EcQF" crossorigin="anonymous"></script>

    <style>
      .bd-placeholder-img {
        font-size: 1.125rem;
        text-anchor: middle;
        -webkit-user-select: none;
        -moz-user-select: none;
        user-select: none;
      }

      @media (min-width: 768px) {
        .bd-placeholder-img-lg {
          font-size: 3.5rem;
        }
      }
    </style>
  </head>
  <body>
'''
    ans += '{}'.format(content)
    ans += '''  </body>
</html>
'''
    return ans


@route('/')
def overview():
    content =  '<h1>Overview</h1><br>'+\
                '<div class="list-group">\
                  <!--a href="/crawl" class="list-group-item">Crawl</a-->\
                  <a href="/album" class="list-group-item active">Album</a>\
                  <a href="/list" class="list-group-item">List</a>\
                  <a href="/exit" class="list-group-item">Exit server</a>\
                </div>'

    return gethtml("Overview", content)

def create_link(file_name, file_path, file_type):
    file_link = file_type
    if file_type == 'MP4':
        file_link = '/video/{}?path={}'.format(file_name, file_path)
    elif file_type == 'PNG':
        file_link = '/image/{}?path={}'.format(file_name, file_path)
    elif file_type == 'JPG' or 'JPEG':
        file_link = '/image/{}?path={}'.format(file_name, file_path)
    return file_link

def load_or_crawl(path=_root_folder, cache_file_path=_cache):
    print('Loading content in {}'.format(path))
    if _files is None:
        try:
            files = load(cache_file_path, path)
            print('Cache loaded')
        except:
            files = crawl_local_path(path)
            print('Cache created')
            store(files, cache_file_path, path)
            print('Cache stored')
        return files
    else:
        return _files

def crawl_local_path(path):
    extensions = ['.mp4', '.png', '.jpg', '.jpeg'] #('.ogg', '.webm')
    files = []

    for root, _, filenames in os.walk(path):
        print('Loading folder: {}'.format(root))
        for filename in filenames:
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in extensions:
                file_path = root
                file_type = file_extension[1:].upper()
                files.append({
                    'name': filename,
                    'path': file_path,
                    'type': file_type,
                    'link': create_link(filename, file_path, file_type),
                })
    sorted_files = sorted(files, key=lambda x: (x['path'], x['name']))
    return sorted_files

def store(array, file_path, crawled_path=_root_folder):
    file_content = json.dumps(array).encode('utf-8')
    checksum = hashlib.md5(file_content).hexdigest()

    with open(file_path, 'w') as file:
        data = {
            'array': array,
            'checksum': checksum,
            'crawled_path': crawled_path
        }
        json.dump(data, file)

def load(cache_file_path, root_folder=_root_folder):
    with open(cache_file_path, 'r') as file:
        data = json.load(file)
        array = data['array']
        checksum = data['checksum']
        crawled_path = data['crawled_path']

        file_content = json.dumps(array).encode('utf-8')
        calculated_checksum = hashlib.md5(file_content).hexdigest()

        if crawled_path != root_folder:
            raise ValueError('Crawled folder mismatch')
        
        if calculated_checksum != checksum:
            raise ValueError('Checksum mismatch for the array')

        return array

@route('/list')
def get_files():
    content =   '<h1>List</h1><br>'+\
                    '<div class="panel-group">'

    files = load_or_crawl(_root_folder)

    # create html here
    path_counts = defaultdict(int)

    for file in files:
        path_counts[file['path']] += 1

    for path, count in path_counts.items():
        m = hashlib.md5()
        m.update(path.encode('utf-8'))
        hashfrompath = m.hexdigest()
        content +=  '<div class="panel panel-default">\
                        <a class="list-group-item" data-toggle="collapse" href="#{}">'.format(hashfrompath)+\
                                '<span class="badge progress-bar-info">{}</span>'.format(count)+\
                            "{}".format(path)+\
                        '</a>'+\
                        '<div class="panel-collapse collapse" id="{}">'.format(hashfrompath)+\
                            '<div class="panel-body">'
        for file in files:
            if file['path'] == path:
                content += '<a href="{}" class="list-group-item">{}</a>'.format(file['link'], file['name'])
        content +=               '</div>\
                            </div>\
                        </div>\
                    </div>\
                </div>'

    return gethtml("All files",
               content)

def image_html(name, path):
  return '''<picture>
  <source srcset="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" media="(max-width: 420px)">
  <img class="card-img-top" src="/image/{0}?path={1}" style="object-fit: contain; min-height: 225px; max-height: 100px; width: auto; max-width: 420px; display: block; margin-left: auto; margin-right: auto;" alt="{0}">
</picture>'''.format(name, path)

def video_html(name, path, is_hidden=False):
    return f'''<video class="w-100" preload="{(lambda x: 'none' if x else 'auto')(is_hidden)}" height="225" muted controls>
  <source src="/file/video/{name}?path={path}" type=\'video/mp4\'>
  <source src="/file/video/{name}?path={path}" type=\'video/ogg\'>
  <source src="/file/video/{name}?path={path}" type=\'video/webm\'>
  Your browser does not support the video tag.
</video>'''

@route('/video/<name>')
def video(name):
    path = request.query.path
    return video_html(name, path)

@route('/file/video/<filename:re:.*\\.(mp4|MP4)>')
def send_video(filename):
    path = request.query.path
    return static_file(filename, root=path)

@route('/ferienplan')
def forward_to():
    return gethtml_bs("Redirect", "redirect", 0, 'https://www.schulferien.org/deutschland/feriendichte/2024/')

@route('/image/<filename:re:.*\\.(png|PNG)>')
def send_image(filename):
    path = request.query.path
    return static_file(filename, root=path, mimetype='image/png')

@route('/image/<filename:re:.*\\.(jpg|jpeg|JPG|JPEG)>')
def send_image(filename):
    path = request.query.path
    return static_file(filename, root=path, mimetype='image/jpg')

def create_album_body(files, index_visible=0, index_hidden=None):
    if index_hidden is None: index_hidden = len(files)
    html = [f'<div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3">']
    
    for i, file in enumerate(files):
        is_hidden = i >= index_hidden
        if is_hidden: 
            hidden_str = 'd-none'
        else:
            hidden_str = 'visible'
        downloadlink_ext=''
        thumbnail_link=image_html(file['name'], file['path'])
        if file['type'] == 'MP4':
            downloadlink_ext='/file'
            thumbnail_link=video_html(file['name'], file['path'], is_hidden)

        html.append(f'''
        <div class="col {hidden_str}">
          <div class="card shadow-sm">
            {thumbnail_link}
            <div class="card-body">
              <p class="card-text">{file['name']}</p>
              <div class="d-flex justify-content-between align-items-center">
                <div class="btn-group">
                  <a href="{file['link']}" class="btn btn-sm btn-outline-secondary" role="button">Open</a>
                  <a href="{downloadlink_ext}{file['link']}" class="btn btn-sm btn-outline-secondary" role="button" download>Download</a>
                  <!--a class="btn btn-sm btn-outline-secondary" id="button{i}" role="button" onclick="copyPathToClip('{file['path']}');">Path to clipboard</a-->
                </div>
                <small class="text-muted" style="height: 40px; width: 200px; overflow: hidden; text-overflow: ellipsis;" >{(lambda x: "[...]"+x[-45:] if len(x) > 50 else x)(file['path'])}</small>
              </div>
            </div>
          </div>
        </div>
        ''')
        # Lambda function trims the path if longer than 50 characters
    
    html.append('</div>')
    return ''.join(html)

@route('/album')
def album():
    files = load_or_crawl(_root_folder)
    body = create_album_body(files, 0, 12)
    content ='''
<header>
  <div class="collapse bg-dark" id="navbarHeader">
    <div class="container">
      <div class="row">
        <div class="col-sm-8 col-md-7 py-4">
          <h4 class="text-white">About</h4>
          <p class="text-muted">Add some information</p>
        </div>
        <div class="col-sm-4 offset-md-1 py-4">
          <h4 class="text-white">Contact</h4>
          <ul class="list-unstyled">
            <li><a href="#" class="text-white">Email me</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  <div class="navbar navbar-dark bg-dark shadow-sm">
    <div class="container">
      <a href="#" class="navbar-brand d-flex align-items-center">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" aria-hidden="true" class="me-2" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
        <strong>Album</strong>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarHeader" aria-controls="navbarHeader" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
    </div>
  </div>
</header>

<main>

  <section id="functional-header" class="py-5 text-center container">
    <div class="row py-lg-5">
      <div class="col-lg-6 col-md-8 mx-auto">
        <h1 class="fw-light">Album example</h1>
        <p class="lead text-muted">Something short and leading</p>
        <p>
          <a href="#" class="btn btn-primary my-2">Main call to action</a>
          <a href="#" class="btn btn-secondary my-2">Secondary action</a>
        </p>
      </div>
    </div>
  </section>
  <div class="album py-5 bg-light" id="visible-album">
    <div class="container">
      {}
    </div>
    <center>
      <button type="button" class="btn btn-sm btn-outline-secondary load-more" style="text-align: center;">Load more</button>
    </center>
  </div>
</main>

<footer class="text-muted py-5">
  <div class="container">
    <p class="float-end mb-1">
      <a href="#">Back to top</a>
    </p>
    <p class="mb-1">Album example </p>
    <p class="mb-0">New to Bootstrap? <a href="/">Visit</a>.</p>
  </div>
</footer>
'''.format(body)
    content += '''
<script>
    var infiniteScrolling = (function() {
      'use strict';

      var limit = 6,
        counter = 0,
        $loading;

      function scrollTo(offset) {
        $(window).scrollTop(offset);
      }

      function loadMore() {
        $('.load-more').after($loading);
        $(document).off('scroll', scrollController);
        $('.load-more').addClass('d-none');

        setTimeout(function() {
          $loading.remove();
          $('.container .row .d-none').slice(0, Math.min(limit, $('.container .row .d-none').length)).each(function() {
            var $this = $(this);
            $this.find('video').attr('preload', 'auto');
            $this.removeClass('d-none');
            $this.addClass('visible');
          });

          $(document).on('scroll touchmove', scrollController);

          if ($('.container .row .d-none').length > 0) {
            $('.load-more').removeClass('d-none');
          } else {
            $('.load-more').addClass('d-none');
          } 

        }, 400);
      }

      function scrollController() {
        if ( ($(window).height() + $(window).scrollTop() + 200) >= ($('header').height() + $('#functional-header').height() + $('#visible-album').height()) && $('.container .row .d-none').length > 0) {
          loadMore();
        }
      }

      function bindUI() {
        $(document).on('scroll', scrollController);
        $('.load-more').on('click', loadMore);
      }

      function init() {
        bindUI();
        $loading = $('<div class="loading" style="text-align: center;">Loading</div>');
      }

      return {
        init: init
      };
    })();

    $(function() {
      infiniteScrolling.init();
    });

    function copyPathToClip(path) {
      // Copy the text inside the text field
      navigator.clipboard.writeText(path);

      // Alert the copied text
      alert("Copied the text: " + path);
    }
</script>
'''
    return gethtml_bs('Album', content)


#Utils
@route('/crawl')
def crawl():
    global _root_folder, _cache
    path = path = request.query.path
    if len(path) > 0:
      _root_folder = path
      files = crawl_local_path(path)
      store(files, _cache, path)
      return gethtml_bs('Crawling', "Crawling path: '{}'".format(path), 5, './')
    else:
      return gethtml_bs('Crawling', "Crawling path invalid: '{}' <br>USE EXAMPLE'/crawl?path=.\images'".format(path), 5, './')

@route('/exit')
def exit():
    print("Exit called")
    os._exit(0)
    return "<h1>System is shutting down!</h1>"

run(host='0.0.0.0', port=8080, debug=False)
