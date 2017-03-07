#!/usr/bin/env python

from bottle import route, run, template, static_file, request
from os import walk

#_video_folder = '../videos'
_video_folder = '.'

@route('/')
def get_files():
    f = []
    for (dirpath, dirnames, filenames) in walk(_video_folder):
        some_filenames = [ file for file in filenames if file.endswith( 
            ('.mp4','.ogg', '.mkv', '.webm')
        ) ]
        f.extend(['{}?path={}'.format(i, dirpath) for i in some_filenames])


    
    result='<h1>All available files in folder</h1><br>'
    for file1 in f:
        result +=  '<a href="{}">{}</a><br>'.format(file1, file1.split('?')[0])
    return result

@route('/<name>')
def index(name):
    path = request.query.path
    return template('\
        <h3>{{name}}</h3><br>\
        <video width="800" height="600" controls>\
          <source src="vid/{{name}}?path={{path}}" type=\'video/mp4\'>\
          <source src="vid/{{name}}?path={{path}}" type=\'video/ogg\'>\
          <source src="vid/{{name}}?path={{path}}" type=\'video/webm\'>\
          Your browser does not support the video tag.\
        </video> ',
    name=name,
    path=path)

@route('/vid/<filename:path>')
def send_video(filename):
    path = request.query.path
    return static_file(filename, root=path)

# Examples
@route('/images/<filename:re:.*\.png>')
def send_image(filename):
    return static_file(filename, root='images', mimetype='image/png')

@route('/hello/<name>')
def hello(name):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='0.0.0.0', port=8080, debug=True)
#run(host='localhost', port=8080, debug=True)