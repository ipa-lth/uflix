#!/usr/bin/env python

from bottle import route, run, template, static_file, request
from collections import defaultdict
import os
from os import walk
import subprocess
import hashlib

_video_folder = '.'

def gethtml(title, content, refresh=None, redirect=None):
    ans = '<html> \
            <head>' +\
              '<title>{}</title>'.format(title) +\
              '<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\
              <!-- jQuery (necessary for Bootstraps JavaScript plugins) --> \
              <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script> \
              <!-- Include all compiled plugins (below), or include individual files as needed --> \
              <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>'
    if refresh:
        ans += '<meta http-equiv="refresh" content="{};'.format(refresh)
        if redirect:
             ans += 'url={}" />'.format(redirect)
        else:
            ans += '"/>'
    ans += '<meta name="viewport" content="width=device-width, initial-scale=1">'
    ans +=  '</head>' + \
            '<body>' + \
            '{}'.format(content) + \
            '</body>' + \
        '</html>'
    return ans

def gethtml5(title, content, refresh=None, redirect=None):
    ans = '''
    <!doctype html>
    <html lang="en">
    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        ''' 
    # if refresh:
    #     ans += '<meta http-equiv="refresh" content="{};'.format(refresh)
    #     if redirect:
    #         ans += 'url={}" />'.format(redirect)
    # ans += '"/>'
    ans += '''
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

        <title>{}</title>
    </head>
    <body>
    '''.format(title) + \
    '{}'.format(content) + \
    '''
        <!-- Optional JavaScript; choose one of the two! -->

        <!-- Option 1: Bootstrap Bundle with Popper -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>

        <!-- Option 2: Separate Popper and Bootstrap JS -->
        <!--
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js" integrity="sha384-IQsoLXl5PILFhosVNubq5LC7Qb9DXgDA9i+tQ8Zj3iwWAwPtgFTxbJ8NT4GN1R8p" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js" integrity="sha384-cVKIPhGWiC2Al4u+LWgxfKTRIcfu0JTxR+EQDz/bgldoEyl4H0zUF0QKbrJ0EcQF" crossorigin="anonymous"></script>
        -->
    </body>
    </html>
    '''
    return ans

def gethtml_bs(title, content, refresh=None, redirect=None):
    if refresh:
        refresh_meta = '<meta http-equiv="refresh" content="{};'.format(refresh)
        if redirect:
            refresh_meta += 'url={}" />'.format(redirect)
        else:
            refresh_meta += '"/>'
    
    ans = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
'''
    ans += '<title>{}</title>'.format(title)
    if refresh:
        refresh_meta = '<meta http-equiv="refresh" content="{};'.format(refresh)
        if redirect:
            refresh_meta += 'url={}" />'.format(redirect)
        else:
            refresh_meta += '"/>'
        ans += refresh_meta
    ans +='''
    <!-- Bootstrap core CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

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
    ans += '''
    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js" integrity="sha384-cVKIPhGWiC2Al4u+LWgxfKTRIcfu0JTxR+EQDz/bgldoEyl4H0zUF0QKbrJ0EcQF" crossorigin="anonymous"></script>
  </body>
</html>
'''
    return ans


@route('/')
def overview():
    content =  '<h1>Overview</h1><br>'+\
                '<div class="list-group">\
                  <!--a href="/crawl" class="list-group-item">Crawl</a-->\
                  <a href="/all" class="list-group-item active">See all videos</a>\
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

def crawl_local_path(path):
    extensions = ['.mp4', '.png', '.jpg', '.jpeg'] #('.ogg', '.webm')
    files = []

    for root, _, filenames in os.walk(path):
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


@route('/all')
def get_files():
    content =   '<h1>All Files</h1><br>'+\
                    '<div class="panel-group">'

    files = crawl_local_path(_video_folder)

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

def video_html(name, path):
    return '''
        <video class="w-100" muted controls>\
          <source src="/file/video/{0}?path={1}" type=\'video/mp4\'>\
          <source src="/file/video/{0}?path={1}" type=\'video/ogg\'>\
          <source src="/file/video/{0}?path={1}" type=\'video/webm\'>\
          Your browser does not support the video tag.\
        </video>'''.format(name, path)

@route('/video/<name>')
def video(name):
    path = request.query.path
    return video_html(name, path)

@route('/file/video/<filename:path>')
def send_video(filename):
    path = request.query.path
    return static_file(filename, root=path)


# Examples
@route('/image/<filename:re:.*\\.png>')
def send_image(filename):
    path = request.query.path
    return static_file(filename, root=path, mimetype='image/png')

@route('/image/<filename:re:.*\\.jpg>')
def send_image(filename):
    path = request.query.path
    return static_file(filename, root=path, mimetype='image/jpg')

def create_album_body(files):
    html = '<div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3">'
    
    for file in files:
        downloadlink_ext=''
        thumbnail_link='''
<img class="img-fluid" 
src="{0}" 
width="100% \9" height="225" 
focusable="false">'''.format(file['link'])
        if file['type'] == 'MP4':
            downloadlink_ext='/file'
            thumbnail_link=video_html(file['name'], file['path'])

        html += '''
        <div class="col">
          <div class="card shadow-sm">
            {4}
            <div class="card-body">
              <p class="card-text">{1}</p>
              <div class="d-flex justify-content-between align-items-center">
                <div class="btn-group">
                  <a href="{0}" class="btn btn-sm btn-outline-secondary" role="button">Open</a>
                  <a href="{3}{0}" class="btn btn-sm btn-outline-secondary" role="button" download>Download</a>
                  <!--button type="button" class="btn btn-sm btn-outline-secondary">View</button-->
                </div>
                <small class="text-muted">{2}</small>
              </div>
            </div>
          </div>
        </div>
        '''.format(file['link'], file['name'], file['path'], downloadlink_ext, thumbnail_link)
    
    html += '</div>'
    return html

@route('/album')
def album():
    files = crawl_local_path(_video_folder)
    body = create_album_body(files)
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

  <section class="py-5 text-center container">
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

  <div class="album py-5 bg-light">
    <div class="container">
      <!--
      <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3">
        <div class="col">
          <div class="card shadow-sm">
            <svg class="bd-placeholder-img card-img-top" width="100%" height="225" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: Thumbnail" preserveAspectRatio="xMidYMid slice" focusable="false"><title>Placeholder</title><rect width="100%" height="100%" fill="#55595c"/><text x="50%" y="50%" fill="#eceeef" dy=".3em">Thumbnail</text></svg>

            <div class="card-body">
              <p class="card-text">This is a wider card with</p>
              <div class="d-flex justify-content-between align-items-center">
                <div class="btn-group">
                  <button type="button" class="btn btn-sm btn-outline-secondary">View</button>
                  <button type="button" class="btn btn-sm btn-outline-secondary">Edit</button>
                </div>
                <small class="text-muted">9 mins</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      -->
      {}
    </div>
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
    return gethtml_bs('Album', content)

#Utils
@route('/exit')
def exit():
    print("Exit called")
    os._exit(0)
    return "<h1>System is shutting down!</h1>"


print('starting in:', os.getcwd())
run(host='0.0.0.0', port=8080, debug=False)
#run(host='localhost', port=8080, debug=True)
