import web
import json
import model
from config import config
from pprint import pprint
import sys
from celltone.celltone import Celltone
import uuid
import subprocess
import os
import os.path

urls = (
    '/', 'Index',
    '/new', 'New',
    '(.+)', 'Program',
    )

class Index(object):
    def GET(self):
        web.header('Content-Type', 'application/json')
        programs = model.get_programs()
        objects = [p.small() for p in programs]
        return json.dumps(objects)

class Program(object):
    def GET(self, id):
        id = id[1:]
        web.header('Content-Type', 'application/json')
        program = model.get_program(id)
        if not program:
            raise web.notfound()
        return json.dumps(program.big())

class New(object):
    def POST(self):
        web.header('Content-Type', 'application/json')
        post = web.input()
        if 'code' not in post:
            raise web.BadRequest()
        code = post['code']
        length = post['length'] if 'length' in post else 60
        id = post['id'] if 'id' in post else str(uuid.uuid4())
        midi_file = config['static_dir'] + '/' + id + '.mid'
        wav_file = config['tmp_dir'] + '/' + id + '.wav'
        mp3_file = config['static_dir'] + '/' + id + '.mp3'
        
        class MyOut:
            def __init__(self):
                self.out = ''
            def write(self, text):
                self.out += text + '\n'
        old_stdout = sys.stdout
        my_out = MyOut()
        sys.stdout = my_out
        ct = Celltone(code, 3, output_file = midi_file,
                      length = length, die_on_error = False, catch_sigint = False)
        ct.start()
        # try:
        #     ct = Celltone(code, 3, output_file = midi_file,
        #                   length = length, die_on_error = False, catch_sigint = False)
        #     ct.start()
        # except Exception, e:
        #     return json.dumps({'celltone_error': str(e)})
        # finally:
        #     sys.stdout = old_stdout

        sys.stdout = old_stdout

        debug = {}
        success = False
        debug['celltone'] = my_out.out
        
        print midi_file

        if os.path.exists(midi_file):
            debug['timidity'] = subprocess.check_output(
                ['timidity', '-Ow', '-o' + wav_file, midi_file], shell = False,
                stderr=subprocess.STDOUT)

        if os.path.exists(wav_file):
            debug['lame'] = subprocess.check_output(
                ['lame', '-b128', wav_file, mp3_file], shell = False,
                stderr=subprocess.STDOUT)
            os.unlink(wav_file)

        if os.path.exists(mp3_file):
            success = True
            model.insert_program(id, code)

        ret = {
            'success': success,
            'debug': debug,
            }
        if success:
            ret['id'] = id

        return json.dumps(ret)

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()

