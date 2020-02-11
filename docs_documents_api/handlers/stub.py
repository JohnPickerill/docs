import hashlib
from sys import getsizeof
from posixpath import join as posixjoin

from flask import  make_response, jsonify, url_for
from docs_documents_api.dependencies.db2_adaptor import Db2
from docs_documents_api.handlers.db2_base import Db2Base
from docs_documents_api.exceptions import ApplicationError


class Stub():

    def __init__(self, app, region, doc_type ):
        self.region = region
        self.doc_type = doc_type
        self.app = app   

    def _return_data(self, adaptor_response, _format ):    
        data = bytearray(b'12345')
        response = make_response(data)
        sha256_actual = hashlib.sha256(data).hexdigest()
        response.headers.set('X-Obj-sha256', sha256_actual)    
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('X-Obj-size', len(data))
        response.headers.set('X-Obj-format', 'APP FORMAT' )
        return response


    def _make_object(self, meta):
        data = b'12345'
        response = {'doc-type': self.doc_type,
                    'title' : meta.pop('TITLE_NO', 'NA').strip(),
                    'document' : 'latest',
                    'doc-version' : meta.pop('FP_VERS_NO', 'NA'),
                    'obj-no' : meta.pop('FP_IMAGE_NO', 'NA'),
                    'obj-uuid': meta.pop('DOC_OBJ_UUID', 'NA'),
                    'obj-state': meta.pop('DOC_OBJ_STATE', 'NA'),
                    'obj-format': meta.pop('FP_IMAGE_FORMAT', 'NA'),
                    'obj-tag': meta.pop('DOC_OBJ_TAG', 'NA'),
                    'obj-hash': meta.pop('DOC_OBJ_HASH', hashlib.sha256(data).hexdigest()),
                    'obj-timestamp': meta.pop('DOC_OBJ_TIMESTAMP', 'NA'),
                    'obj-state-age' : meta.pop('OBJ_STATE_AGE', '-1'),
                    'obj-state-change' : meta.pop('DOC_OBJ_STATECHANGE', 'none'),
                    'obj-size': meta.pop('DOC_OBJ_SIZE','NA'),
                    }
        response['obj-metadata'] = meta
        response['obj-MIME'] = 'application/octet-stream' 

        if response.get('obj-state') not in ['stored']:
            path = url_for('object_api._get_object_data',
                            region = self.region,
                            doc_type = 'titleplan',
                            title = response['title'],
                            document = 'latest',
                            version = response['doc-version'],
                            object_no = response['obj-no']
                            )
            if path.startswith('/'):
                path = path[1:]
            response['obj-staged-url'] = posixjoin(self.app.config["DOCS_API_URL"], path)
            response['obj-url'] = 'https://www.python.org/static/img/python-logo.png'
        return response


    def _make_objects(self, objects):
        results = []
        for _object in objects:    
            results.append(self._make_object(_object))
        return results


    def test_error(self, title):
 
        if 'NOTFOUND' in title:
            raise ApplicationError(title,'NOTFOUND', 404, True)   
        elif 'BADREQUEST' in title:
            raise ApplicationError(title,'BADREQUEST', 400, True)         
        elif 'FORBIDDEN' in title:
                raise ApplicationError(title,'FORBIDDEN', 403, True) 
        elif 'SYSERROR' in title:
                raise ApplicationError(title,'SYSERROR', 500, True)         
 



# ==========================================    

    def get_titles(self, start=None, size=None):
        titles = ['title1','title2']  
        return jsonify(titles)
 
    def get_versions(self, title, document):
        self.test_error(title)
        versions = ['1000','1001']  
        return jsonify(versions)

    def get_objects(self, title, document, version):
        self.test_error(title)
        obj1 = {'FP_DATA1': 'Silly data',
                'FP_DATA2': 'More Silly Data'}
        obj2 = dict(obj1)        
        objects = self._make_objects([obj1, obj2])
        return jsonify(objects)

    def get_object(self, title, document, version, image):
        self.test_error(title)
        obj1 = {'FP_DATA1': 'Silly data',
                'FP_DATA2': 'More Silly Data'}
        meta = self._make_object(obj1)
        return jsonify(meta)

    def get_uuid_object(self, uuid):
        self.test_error(title)
        meta = self._make_object({})
        return jsonify(meta)

    def get_objects_in_state(self, state, size):
        self.test_error(title)
        objects = self._make_objects([{},{}])    
        return jsonify(objects)

    # ===============

    def get_data(self, uuid):
        self.test_error(title)
        return self._get_data(None )

    def get_data(self, title, document, version, obj_no):
        self.test_error(title)
        return self._get_data(None)


    def _get_data(self, object_info):
        return self._return_data(None, None)

 