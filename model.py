import web
from config import config

db = web.database(dbn = config['dbn'], user = config['db_user'],
                  pw = config['db_pass'], db = config['db_name'])

def get_programs():
    programs = db.select('programs', order = 'date_created DESC')
    return [Program(p) for p in programs]

def get_program(id):
    programs = db.select('programs', where = 'id = $id', vars = locals())
    if len(programs):
        return Program(programs[0])
    return None

def insert_program(id, code):
    db.query('REPLACE INTO programs (id, code) VALUES ($id, $code)',
             vars = locals())

class Program:
    def __init__(self, storage):
        self.id = storage.id
        self.code = storage.code
        self.date_created = storage.date_created
        self.permalink = config['web_url'] + '#' + self.id
        self.mp3 = config['server_url'] + '/static/' + self.id + '.mp3'
        self.midi = config['server_url'] + '/static/' +self.id + '.mid'

    def small(self):
        return {
            'id': self.id,
            'date_created': self.date_created.isoformat(),
            'permalink': self.permalink,
            }

    def big(self):
        return {
            'id': self.id,
            'code': self.code,
            'permalink': self.permalink,
            'mp3': self.mp3,
            'midi': self.midi,
            'date_created': self.date_created.isoformat(),
            }
