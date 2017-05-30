#!/usr/bin/env python

from bottle import route, run, template, static_file, request
import os
from os import walk

from thread import start_new_thread
import subprocess
import hashlib

_video_folder = '.'

_ffmpeg_folder = 'h:\\'

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

@route('/')
def overview():
    content =  '<h1>Overview</h1><br>'+\
                '<div class="list-group">\
                  <a href="/all" class="list-group-item active">See all videos</a>\
                  <a href="/shutdown" class="list-group-item">Shut down server</a>\
                  <a href="/shutdown/abort" class="list-group-item">Abort shutdown</a>\
                </div>'

    return gethtml("Overview", content)

@route('/all')
def get_files():
    content =   '<h1>All Videos</h1><br>'+\
                    '<div class="panel-group">'

    compile_files = []
    for (dirpath, dirnames, filenames) in walk(_video_folder):
        webvideo_files = [file for file in filenames if (file.endswith(
            ('.mp4','.ogg', '.webm')
        ) and
            not file.startswith("_")
        )]
        webvideo_links = ['{}?path={}'.format(i, dirpath) for i in webvideo_files]
        compile_files.extend([file for file in filenames if (file.endswith('.mp4') and
            file.startswith("_"))])

        avi_files = [file for file in filenames if file.endswith(('.avi', '.mkv'))]
        avi_files_tmp = [file for file in filenames if file.endswith(('.avi', '.mkv'))]
        
        avi_links = ['/convert/{}?path={}'.format(avi, dirpath) for avi in avi_files]
        compile_cnt = 0
        for avi in avi_files_tmp: #Use a inplace copy to iterate to avoid multiple arrays
            if (('{}.mp4'.format(avi) in webvideo_files) or ('_{}.mp4'.format(avi) in compile_files)):
                #print avi
                avi_files.remove(avi)
                avi_links.remove('/convert/{}?path={}'.format(avi, dirpath))
                if '_{}.mp4'.format(avi) in compile_files:
                    compile_cnt += 1
        #    else:
        #        avi_links.extend(['/convert/{}?path={}'.format(avi, dirpath)])

        # create html here
        if (len(webvideo_files) + len(avi_files)) != 0:
            m = hashlib.md5()
            m.update(dirpath)
            hashfrompath = m.hexdigest()
            content +=  '<div class="panel panel-default">\
                            <a class="list-group-item" data-toggle="collapse" href="#{}">'.format(hashfrompath)+\
                                '<span class="badge progress-bar-warning">{}</span>'.format(compile_cnt)+\
                                '<span class="badge progress-bar-danger">{}</span>'.format(len(avi_files))+\
                                '<span class="badge progress-bar-info">{}</span>'.format(len(webvideo_files))+\
                                "{}".format(dirpath)+\
                            '</a>'+\
                            '<div class="panel-collapse collapse" id="{}">'.format(hashfrompath)+\
                                '<div class="panel-body">'
            for vid, link in zip(webvideo_files, webvideo_links):
                content += '<a href="{}" class="list-group-item active">{}</a>'.format(link, vid)

            for avi, link in zip(avi_files, avi_links):
                content += '<a href="{}" class="list-group-item">{}</a>'.format(link, avi)

            content +=          '</div>\
                            </div>\
                        </div>\
                    </div>\
                </div>'
    return gethtml("All files",
               content)

@route('/all-medialist')
def get_files():
    result='<h1>All available files</h1><br>'+\
           '<div class="vids">\
                    <ul class="media-list">'

    for (dirpath, dirnames, filenames) in walk(_video_folder):
        webvideo_files = [file for file in filenames if (file.endswith(
            ('.mp4','.ogg', '.mkv', '.webm')
        ) and
            not file.startswith("_")
        )]
        webvideo_links = ['{}?path={}'.format(i, dirpath) for i in webvideo_files]

        avi_files = [file for file in filenames if file.endswith('.avi')]
        avi_links = []
        for avi in avi_files:
            if not "{}.mp4".format(avi) in webvideo_files:
                avi_links.extend(['/convert/{}?path={}'.format(avi, dirpath)])
            else:
                avi_files.remove(avi)

        # create html here
        if len(webvideo_files) != 0 and len(avi_files) != 0:
            result += '<li class="media">\
                            <a class="pull-left" href="#"> \
                                <span class="glyphicon glyphicon-folder-open" \
                                      style="width: 64px; height: 64px;" \
                                      aria-hidden="true">\
                                </span>\
                                <!--img class="media-object" alt="[[img alt tag]]" style="width: 20px; height: 20px;" src="[[img url]]" /-->\
                            </a>\
                            <div class="media-body">'+\
                                '<h4 class="media-heading">{}</h4>'.format(dirpath)

            # Nested media object
            for vid, link in zip(webvideo_files, webvideo_links):
                result +=   '<div class="media">\
                                  <a class="pull-left pull-middle" href="{}">'.format(link) +\
                                      '<span class="glyphicon glyphicon-play" \
                                            style="width: 64px; height: 64px;" \
                                            aria-hidden="true">\
                                      </span>\
                                      <!--img class="media-object" alt="[[img alt tag]]" style="width: 64px; height: 64px;" src="[[img url]]" /-->\
                                  </a>\
                                  <div class="media-body">'+\
                                  '<h4 class="media-heading">{}</h4>'.format(vid)+\
                                  '</div>\
                              </div>'

            for avi, link in zip(avi_files, avi_links):
                result +=   '<div class="media">\
                                  <a class="pull-left pull-middle" href="{}">'.format(link) +\
                                      '<span class="glyphicon glyphicon-record" \
                                            style="width: 64px; height: 64px;" \
                                            aria-hidden="true">\
                                      </span>\
                                      <!--img class="media-object" alt="[[img alt tag]]" style="width: 64px; height: 64px;" src="[[img url]]" /-->\
                                  </a>\
                                  <div class="media-body">'+\
                                  '<h4 class="media-heading">{}</h4>'.format(avi)+\
                                  '</div>\
                              </div>'
            result +=     '</div>\
                     </li>'

    return gethtml("All files",
                   result)

@route('/test')
def medialist():
    content = '<div class="vids">\
                    <ul class="media-list">\
                        <li class="media">\
                            <a class="pull-left" href="#"> \
                                <span class="glyphicon glyphicon-play" \
                                      style="width: 64px; height: 64px;" \
                                      aria-hidden="true">\
                                </span>\
                                <!--img class="media-object" alt="[[img alt tag]]" style="width: 64px; height: 64px;" src="[[img url]]" /-->\
                            </a>\
                            <div class="media-body">\
                                <h4 class="media-heading">Media heading</h4>\
                                <p>[[media caption]]</p>\
                                    <!-- Nested media object -->\
                                    <div class="media"><a class="pull-left" href="#"> <img class="media-object" alt="[[img alt tag]]" style="width: 64px; height: 64px;" src="[[img url]]" /> </a>\
                                        <div class="media-body">\
                                        <h4 class="media-heading">Nested media heading</h4>\
                                        [[media caption]]</div>\
                                    </div>\
                            </div>\
                        </li>\
                    </ul>\
                </div>'
    return gethtml("", content)

@route('/<name>')
def index(name):
    path = request.query.path
    return template('\
        <h3>{{name}}</h3><br>\
        <video width="800" height="600" preload="auto" controls>\
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

def compileThread(path, name):
    ans = '{}ffmpeg -i "{}" '.format(_ffmpeg_folder, path+'\\'+name) + \
        '-vcodec libx264 -pix_fmt yuv420p ' + \
        '-profile:v baseline -preset slower -crf 18 ' + \
        '-vf "scale=trunc(in_w/2)*2:trunc(in_h/2)*2" '+ \
        '"_{}.mp4"'.format(name)
    subprocess.call(ans)

    new_name = '{}.mp4'.format(name)

    os.rename(os.path.join(os.getcwd(), '_'+new_name),
              os.path.join(os.getcwd(), path, new_name))

@route('/convert/<name>')
def convert(name):
    path = request.query.path
#    ans =  '{}ffmpeg -i "{}" '.format(_ffmpeg_folder, path+'\\'+name) + \
#            '-vcodec libx264 -pix_fmt yuv420p ' + \
#            '-movflags frag_keyframe+empty_moov ' + \
#            '-profile:v baseline -preset slower -crf 18 ' + \
#            '-vf "scale=trunc(in_w/2)*2:trunc(in_h/2)*2" '+ \
#            '"{}.mp4"'.format(os.path.splitext(name)[0])
    start_new_thread(compileThread, (path, name))
    return gethtml("Conversion",
                   '<h3>Converting {} @ {}<br>Returning in 10 sec</h3>'.format(name, path),
                   10,
                   '/all')

#            '<html>' + \
#                '<head>' + \
#                  '<title>Convertion</title>' + \
#                  '<meta http-equiv="refresh" content="2; url=/all" />' + \
#                '</head>' + \
#                '<body>' + \
#                '<h3>Converting {} @ {}<br>Returning in 2 sec</h3>'.format(name, path) + \
#                '</body>' + \
#            '</html>'

# Examples
@route('/list')
def list():
    content = '<div class="list-group">\
                  <a href="#" class="list-group-item">\
                    Cras justo odio\
                  </a>\
                  <a href="#" class="list-group-item">Dapibus ac facilisis in</a>\
                  <a href="#" class="list-group-item">Morbi leo risus</a>\
                  <a href="#" class="list-group-item">Porta ac consectetur ac</a>\
                  <a href="#" class="list-group-item">Vestibulum at eros</a>\
                </div>'
    return gethtml('list', content)

@route('/panelgroup')
def panel():
    content =   '<h1>Bootstrap Panel with Collapsable Sub-List Group</h1>\
                    <div class="panel-group">\
                        \
                        <div class="panel panel-default">\
                            <a class="list-group-item" data-toggle="collapse" href="#collapseTC001A">\
                                <span class="badge">4</span>\
                                TC001A\
                            </a>\
                            <div class="panel-collapse collapse" id="collapseTC001A">\
                                <div class="panel-body">\
                                    <a href="#" class="list-group-item">4</a>\
                                    <a href="#" class="list-group-item">3</a>\
                                    <a href="#" class="list-group-item">2</a>\
                                    <a href="#" class="list-group-item">1</a>\
                                </div>\
                            </div>\
                        </div>\
                        \
                        <div class="panel panel-default">\
                            <a class="list-group-item" data-toggle="collapse" href="#collapseTC002A">\
                                <span class="badge">2</span>\
                                TC002A\
                            </a>\
                            <div class="panel-collapse collapse" id="collapseTC002A">\
                                <div class="panel-body">\
                                    <a href="#" class="list-group-item">2</a>\
                                    <a href="#" class="list-group-item">1</a>\
                                </div>\
                            </div>\
                        </div>\
                    </div>'
    return gethtml('list', content)

@route('/images/<filename:re:.*\.png>')
def send_image(filename):
    return static_file(filename, root='images', mimetype='image/png')

@route('/hello/<name>')
def hello(name):
    return template('<b>Hello {{name}}</b>!', name=name)

#Utils
@route('/shutdown')
def shutdown():
    subprocess.call(["shutdown", "/s"])
    return "<h1>System is shutting down!</h1>"

@route('/shutdown/abort')
def no_shutdown():
    subprocess.call(["shutdown", "/a"])
    return "<h1>Aborting shutdown!</h1>"

print 'starting in:', os.getcwd()
run(host='0.0.0.0', port=8080, debug=False)
#run(host='localhost', port=8080, debug=True)
