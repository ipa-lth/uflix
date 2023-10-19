#!/usr/bin/env python

from bottle import route, run, template, static_file, request
from collections import defaultdict
import os
from os import walk
import subprocess
import hashlib

_video_folder = '.\\images'

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

@route('/')
def overview():
    content =  '<h1>Overview</h1><br>'+\
                '<div class="list-group">\
                  <a href="/crawl" class="list-group-item">Crawl</a>\
                  <a href="/all" class="list-group-item active">See all videos</a>\
                  <a href="/exit" class="list-group-item">Shut down server</a>\
                </div>'

    return gethtml("Overview", content)

def crawl(video_folder):
    webvideo_files = []
    webvideo_links = []
    for (dirpath, dirnames, filenames) in os.walk(video_folder):
        webvideo_files.extend([file for file in filenames if file.endswith(('.mp4', '.ogg', '.webm'))])
        webvideo_links.extend(['/video/{}?path={}'.format(i, dirpath) for i in webvideo_files])
    return webvideo_files, webvideo_links

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
    extensions = ['.mp4', '.png', '.jpg', '.jpeg']
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

def store(webvideo_files, webvideo_links, filename):
    with open(filename, 'w') as file:
        file.write('\n'.join(webvideo_files) + '\n')
        file.write('\n'.join(webvideo_links) + '\n')
        checksum = hashlib.md5('\n'.join(webvideo_files + webvideo_links).encode()).hexdigest()
        file.write(checksum)

def load(filename):
    webvideo_files = []
    webvideo_links = []
    stored_checksum = ''
    with open(filename, 'r') as file:
        lines = file.readlines()
        webvideo_files = lines[0].strip().split('\n')
        webvideo_links = lines[1].strip().split('\n')
        stored_checksum = lines[2].strip()

    computed_checksum = hashlib.md5('\n'.join(webvideo_files + webvideo_links).encode()).hexdigest()
    if stored_checksum == computed_checksum:
        return webvideo_files, webvideo_links
    else:
        raise ValueError('Checksum mismatch. The stored file may have been modified.')

@route('/crawl')
def cache():
    webvideo_files, webvideo_links = crawl(_video_folder)
    store(webvideo_files, webvideo_links, "_cache.uflix")
    return

@route('/all')
def get_files():
    content =   '<h1>All Files</h1><br>'+\
                    '<div class="panel-group">'

    files = crawl_local_path(_video_folder)
    # try:
    #     webvideo_files, webvideo_links = load("_cache.uflix")
    # except:
    #     webvideo_files, webvideo_links = crawl(_video_folder)
    #     store(webvideo_files, webvideo_links, "_cache.uflix")

    # for (dirpath, dirnames, filenames) in walk(_video_folder):
    #     webvideo_files = [file for file in filenames if file.endswith(('.mp4','.ogg', '.webm'))] # not  '.avi', '.mkv'
    #     webvideo_links = ['/video/{}?path={}'.format(i, dirpath) for i in webvideo_files]

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


# @route('/all-medialist')
# def get_files():
#     result = '<h1>All available files</h1><br>' + \
#              '<div class="vids">' + \
#              '<ul class="media-list">'

#     for (dirpath, dirnames, filenames) in walk(_video_folder):
#         webvideo_files = [file for file in filenames if file.endswith(('.mp4', '.ogg', '.mkv', '.webm'))]
#         print(webvideo_files)
#         webvideo_links = ['/video/{}?path={}'.format(i, dirpath) for i in webvideo_files]
#         print(webvideo_links)

#         if len(webvideo_files) != 0:
#             result += f'<li class="media"> \
#                             <a class="pull-left" href="#"> \
#                                 <span class="glyphicon glyphicon-folder-open" \
#                                       style="width: 64px; height: 64px;" \
#                                       aria-hidden="true"> \
#                                 </span> \
#                             </a> \
#                             <div class="media-body"> \
#                                 <h4 class="media-heading">{dirpath}</h4>'

#             for vid, link in zip(webvideo_files, webvideo_links):
#                 result += f'<div class="media"> \
#                                 <a class="pull-left pull-middle" href="{link}"> \
#                                     <span class="glyphicon glyphicon-play" \
#                                           style="width: 64px; height: 64px;" \
#                                           aria-hidden="true"> \
#                                     </span> \
#                                 </a> \
#                                 <div class="media-body"> \
#                                     <h4 class="media-heading">{vid}</h4> \
#                                 </div> \
#                             </div>'

#             result += '</div> \
#                      </li>'

#     return gethtml("All files", result)

@route('/video/<name>')
def index(name):
    path = request.query.path
    return template('\
        <h3>{{name}}</h3><br>\
        <video width="800" height="600" preload="auto" controls>\
          <source src="/video/play/{{name}}?path={{path}}" type=\'video/mp4\'>\
          <source src="/video/play/{{name}}?path={{path}}" type=\'video/ogg\'>\
          <source src="/video/play/{{name}}?path={{path}}" type=\'video/webm\'>\
          Your browser does not support the video tag.\
        </video> ',
    name=name,
    path=path)

@route('/video/play/<filename:path>')
def send_video(filename):
    path = request.query.path
    return static_file(filename, root=path)

# Examples

@route('/image/<filename:re:.*\.png>')
def send_image(filename):
    path = request.query.path
    return static_file(filename, root=path, mimetype='image/png')

@route('/image/<filename:re:.*\.jpg>')
def send_image(filename):
    path = request.query.path
    return static_file(filename, root=path, mimetype='image/jpg')

@route('/hello/<name>')
def hello(name):
    return template('<b>Hello {{name}}</b>!', name=name)

def generate_lightbox_code(files):
    html_code = '<div class="lightbox">\n'
    html_code += '  <div class="row">\n'
    
    # Iterate over the files and create the HTML code for each image
    for file in files:
        html_code += '    <div class="col-lg-6">\n'
        html_code += f'      <img src="{file["link"]}" data-mdb-img="{file["link"]}" alt="{file["name"]}" class="w-100 mb-2 mb-md-4 shadow-1-strong rounded" />\n'
        html_code += '    </div>\n'
    
    html_code += '  </div>\n'
    html_code += '</div>'
    
    return html_code

def generate_html_gallery(files):
    html_code = '<!-- Gallery -->\n'
    html_code += '<div class="row">\n'
    
    # Iterate over the files and create the HTML code for each image
    for file in files:
        html_code += '  <div class="col-lg-4 col-md-12 mb-4 mb-lg-0">\n'
        html_code += f'    <img src="{file["link"]}" class="w-100 shadow-1-strong rounded mb-4" alt="{file["name"]}" />\n'
        html_code += '  </div>\n'
    
    html_code += '</div>\n'
    html_code += '<!-- Gallery -->'
    
    return html_code

def generate_html_carousel(files):
    html_code = '<!-- Carousel wrapper -->\n'
    html_code += '<div id="carouselMultiItemExample" class="carousel slide carousel-dark text-center" data-mdb-ride="carousel">\n'
    html_code += '  <!-- Controls -->\n'
    html_code += '  <div class="d-flex justify-content-center mb-4">\n'
    html_code += '    <button class="carousel-control-prev position-relative" type="button" data-mdb-target="#carouselMultiItemExample" data-mdb-slide="prev">\n'
    html_code += '      <span class="carousel-control-prev-icon" aria-hidden="true"></span>\n'
    html_code += '      <span class="visually-hidden">Previous</span>\n'
    html_code += '    </button>\n'
    html_code += '    <button class="carousel-control-next position-relative" type="button" data-mdb-target="#carouselMultiItemExample" data-mdb-slide="next">\n'
    html_code += '      <span class="carousel-control-next-icon" aria-hidden="true"></span>\n'
    html_code += '      <span class="visually-hidden">Next</span>\n'
    html_code += '    </button>\n'
    html_code += '  </div>\n'
    html_code += '  <!-- Inner -->\n'
    html_code += '  <div class="carousel-inner py-4">\n'

    # Divide the files into groups of 3
    groups = [files[i:i+3] for i in range(0, len(files), 3)]

    # Iterate over the groups and create the HTML code for each carousel item
    for i, group in enumerate(groups):
        if i == 0:
            html_code += '    <!-- Single item -->\n'
            html_code += '    <div class="carousel-item active">\n'
        else:
            html_code += '    <!-- Single item -->\n'
            html_code += '    <div class="carousel-item">\n'

        html_code += '      <div class="container">\n'
        html_code += '        <div class="row">\n'

        # Iterate over the files in the group and create the HTML code for each card
        for file in group:
            html_code += '          <div class="col-lg-4">\n'
            html_code += '            <div class="card">\n'
            html_code += f'              <img src="{file["link"]}" class="card-img-top" alt="{file["name"]}" />\n'
            html_code += '              <div class="card-body">\n'
            html_code += f'                <h5 class="card-title">{file["name"]}</h5>\n'
            html_code += f'                <p class="card-text">{file["path"]}</p>\n'
            html_code += '                <a href="#!" class="btn btn-primary">Button</a>\n'
            html_code += '              </div>\n'
            html_code += '            </div>\n'
            html_code += '          </div>\n'

        html_code += '        </div>\n'
        html_code += '      </div>\n'
        html_code += '    </div>\n'

    html_code += '  </div>\n'
    html_code += '  <!-- Inner -->\n'
    html_code += '</div>\n'
    html_code += '<!-- Carousel wrapper -->'

    return html_code

@route('/light')
def light():
    files = crawl_local_path(_video_folder)
    content = generate_html_gallery(files)
    return gethtml5('title', content)

@route('/carousel')
def light():
    files = crawl_local_path(_video_folder)
    content = generate_html_carousel(files)
    return gethtml5('carousel', content)

@route('/lightbox')
def lightbox():
    files = crawl_local_path(_video_folder)
    content ='\
<div class="lightbox">\
  <div class="row">\
    <div class="col-lg-6">\
      <img\
        src="https://mdbcdn.b-cdn.net/img/Photos/Thumbnails/Slides/1.webp"\
        data-mdb-img="https://mdbcdn.b-cdn.net/img/Photos/Slides/1.webp"\
        alt="Table Full of Spices"\
        class="w-100 mb-2 mb-md-4 shadow-1-strong rounded"\
      />\
      <img\
        src="https://mdbcdn.b-cdn.net/img/Photos/Thumbnails/Square/1.webp"\
        data-mdb-img="https://mdbcdn.b-cdn.net/img/Photos/Square/1.webp"\
        alt="Coconut with Strawberries"\
        class="w-100 shadow-1-strong rounded"\
      />\
    </div>\
    <div class="col-lg-6">\
      <img\
        src="https://mdbcdn.b-cdn.net/img/Photos/Thumbnails/Vertical/1.webp"\
        data-mdb-img="https://mdbcdn.b-cdn.net/img/Photos/Vertical/1.webp"\
        alt="Dark Roast Iced Coffee"\
        class="w-100 shadow-1-strong rounded"\
      />\
    </div>\
  </div>\
</div>'
    return gethtml5("Lightbox", content)

#Utils
@route('/exit')
def exit():
    os._exit(0)
    return "<h1>System is shutting down!</h1>"

