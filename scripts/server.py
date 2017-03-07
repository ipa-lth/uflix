#!/usr/bin/env python

from bottle import route, run, template
from bottle import static_file

from os import listdir
from os.path import isfile, join

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/images/<filename:re:.*\.png>')
def send_image(filename):
    return static_file(filename, root='images', mimetype='image/png')

@route('/<name>')
def index(name):
    return template('\
        <h3>{{name}}</h3><br>\
        <video width="800" height="600" controls>\
          <source src="videos/{{name}}" type=\'video/mp4\'>\
        Your browser does not support the video tag.\
        </video> ',
    name=name)

@route('/videos/<filename:re:.*\.mp4>')
def send_video(filename):
    return static_file(filename, root='videos', mimetype='video/mp4')

@route('/files')
def get_files():
    onlyfiles = [f for f in listdir('videos') if isfile(join('videos', f))]
    result='<h1>All available files in folder</h1><br>'
    for file1 in onlyfiles:
        result +=  '<a href="{}">{}</a><br>'.format(file1, file1)
    return result

run(host='0.0.0.0', port=8080, debug=True)
#run(host='localhost', port=8080, debug=True)