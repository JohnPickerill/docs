from sys import getsizeof
from posixpath import join as posixjoin

from flask import  make_response, jsonify, url_for
from docs_documents_api.dependencies.db2_adaptor import Db2
from docs_documents_api.handlers.db2_base import Db2Base
from docs_documents_api.exceptions import ApplicationError

class Db2_retained(Db2Base):



    def _make_object(self, meta):
        response = self.get_obj_labels(meta)
        response.update({'title' : meta.pop('TITLE_NO', 'NA').strip(),
                    'document' : meta.pop('DEED_NO', 'NA'),
                    'doc-version' : 'latest',
                    'obj-no' : meta.pop('DEED_PAGE_NO', 'NA'),
                    'obj-format': meta.pop('DEED_PAGE_FORMAT'),
                 })
        response['obj-metadata'] = meta
        response['obj-MIME'] = self.MIME.get(response['obj-format'], 'application/octet-stream')         

        if response['obj-state'] not in ['stored']: 
            path = url_for('object_api._get_object_data',
                region = self.region,
                doc_type = self.doc_type,
                title = response['title'],
                document = response['document'],
                version = response['doc-version'],
                object_no = response['obj-no'])
            if path.startswith('/'):
                path = path[1:]
            response['obj-staged-url'] = posixjoin(self.app.config["DOCS_API_URL"], path)   

        if response['obj-state'] in ['stored', 'acquired']:
            response['obj-url'] = posixjoin(self.app.config["OBJ_API_URL"], self.region, 'objects', self.doc_type, 'uuids', response['obj-uuid'])
        else:
            response['obj-url'] = response['obj-staged-url']
            
        response['obj-MIME'] = self.MIME.get(response['obj-format'],'application/octet-stream')    
        response['obj-metadata']= meta
        return response


# ==========================================  



    def get_objects(self, title, doc_no, version):
        objects = self._make_objects(self.db2.get_retained_pages(title, doc_no))
        return jsonify(objects)

    def get_object(self, title, doc_no, version, obj_no):
        meta = self.db2.get_retained_page_meta(title, doc_no, obj_no)
        meta = self._make_object(meta)
        return jsonify(meta)



    # ==================

    def get_data(self, uuid):
        image_info = self.db2.get_retained_uuid(uuid) 
        return self._get_data(image_info)

    def get_data(self, title, document, version, obj_no):
        image_info = self.db2.get_retained_page_meta(title, document, obj_no)
        return self._get_data(image_info )


    def _get_data(self, object_info):
        self.app.logger.debug(object_info)
        title = object_info["TITLE_NO"]
        deed = object_info["DEED_NO"]
        page = object_info["DEED_PAGE_NO"]
        _format = object_info['DEED_PAGE_FORMAT'].strip()
        adaptor_response = self.db2.get_retained_data(title, deed, page)
        return self._return_data(adaptor_response, _format)


