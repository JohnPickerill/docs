import hashlib
from abc import abstractmethod
from sys import getsizeof

from flask import  make_response, jsonify, url_for

from docs_documents_api.dependencies.db2_adaptor import Db2
from docs_documents_api.exceptions import ApplicationError


class Db2Base:
    
    MIME = {'JPG' :     'image/jpeg',
            'MRD' :     'image/tiff',
            'SIS' :     'image/tiff',
            'TIF' :     'image/tiff',
            'A3 JPEG' : 'image/jpeg',
            'A3 TIFF' : 'image/tiff',
            'A4 GIF' :  'image/gif',
            'A4 JPEG' : 'image/jpeg',
            'A4 TIFF' : 'image/tiff',
            'JPG' :     'image/jpeg',
            'OVERSIZE' :'application/octet-stream',
            'PDF' :     'application/pdf',
            'TESTDATA' : 'application/octet-stream'}

    def __init__(self, app, region, doc_type ):
        self.region = region
        self.doc_type = doc_type
        self.db2 = Db2(app,
                        app.config[self.region + "_ADAPTOR_URL"],
                        app.config[self.region + "_ADAPTOR_KEY"])
        self.app = app    

    def uncomment(self, val):
        if val is not None:
            val =  val[1:] if val.startswith('#') else val 
        return val

    def get_obj_labels(self, meta):
        return {'doc-type': self.doc_type,
                'obj-uuid': meta.pop('DOC_OBJ_UUID', 'NA'),
                'obj-state': self.uncomment(meta.pop('DOC_OBJ_STATE', 'NA')),
                'obj-tag': meta.pop('DOC_OBJ_TAG', 'NA'),
                'obj-hash': meta.pop('DOC_OBJ_HASH'),
                'obj-timestamp': meta.pop('DOC_OBJ_TIMESTAMP', 'NA'),
                'obj-state-age' : meta.pop('OBJ_STATE_AGE', '-1'),
                'obj-state-change' : meta.pop('DOC_OBJ_STATECHANGE', 'none'),
                'obj-size': meta.pop('DOC_OBJ_SIZE','NA'),
                }

    def _return_data(self, adaptor_response, _format ):    
        data = adaptor_response.content
        response = make_response(data)
        sha256_actual = hashlib.sha256(data).hexdigest()
        sha256_expected = adaptor_response.headers.get('X-Obj-sha256') or sha256_actual
        if sha256_actual != sha256_expected:
            raise ApplicationError("CHECKSUM ERROR", "CHECKSUM", 500, True)
        else:
            self.app.logger.debug('========== Checksum OK =======')
        response.headers.set('X-Obj-sha256', sha256_actual)    
        response.headers.set('Content-Type', self.MIME.get(_format, 'application/octet-stream' ))
        response.headers.set('X-Obj-size', getsizeof(data))
        response.headers.set('X-Obj-format', _format)
        response.headers.set('X-Obj-tag', 'DB2-tag' )
        return response
        


    @abstractmethod    
    def make_object(self): 
        pass   

    def _make_objects(self, objects):    
        results = []
        for _object in objects:    
            results.append(self._make_object(_object))
        return results
 
    def get_titles(self, start=None, size=None):
        titles = self.db2.get_titles(self.doc_type, start, size)
        return jsonify(titles)

    def get_documents(self, title, start=None, size=None):
        docs = self.db2.get_documents(self.doc_type, title, start, size)
        return jsonify(docs)

    def get_document(self, title, doc_no):
        doc = self.db2.get_document_meta(self.doc_type, title, doc_no)
        return jsonify(doc)

    def get_objects_in_state(self, state, size):
        objects = self._make_objects(self.db2.get_objects_in_state(self.doc_type, state, size))    
        return jsonify(objects)