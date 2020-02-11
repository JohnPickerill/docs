
from posixpath import join as posixjoin

from flask import  make_response, jsonify, url_for
from docs_documents_api.dependencies.db2_adaptor import Db2
from docs_documents_api.handlers.db2_base import Db2Base
from docs_documents_api.exceptions import ApplicationError


class Db2_titleplan(Db2Base):


    def _make_object(self, meta):
        response = self.get_obj_labels(meta)
        response.update({ 
                    'title' : meta.pop('TITLE_NO', 'NA').strip(),
                    'document' : 'latest',
                    'doc-version' : meta.pop('FP_VERS_NO', 'NA'),
                    'obj-no' : meta.pop('FP_IMAGE_NO', 'NA'),
                    'obj-format': meta.pop('FP_IMAGE_FORMAT'),              
                    })
        response['obj-metadata'] = meta
        response['obj-MIME'] = self.MIME.get(response['obj-format'], 'application/octet-stream')

        if response['obj-state'] not in ['stored']:
            path = url_for('object_api._get_object_data',
                            region = self.region,
                            doc_type = self.doc_type,
                            title = response['title'],
                            document = 'latest',
                            version = response['doc-version'],
                            object_no = response['obj-no']
                            )
            if path.startswith('/'):
                path = path[1:]
            response['obj-staged-url'] = posixjoin(self.app.config["DOCS_API_URL"], path)   

        if response['obj-state'] in ['stored', 'acquired']:
            response['obj-url'] = posixjoin(self.app.config["OBJ_API_URL"], self.region, "objects", self.doc_type, "uuids", response['obj-uuid'])
        else:
            response['obj-url'] = response['obj-staged-url']

 
        return response






# ==========================================    


    def get_versions(self, title, document):
        versions = self.db2.get_titleplan_versions(title)    
        return jsonify(versions)

    def get_objects(self, title, document, version):
        objects = self._make_objects(self.db2.get_titleplan_images_meta(title, version))
        return jsonify(objects)

    def get_object(self, title, document, version, image):
        meta = self._make_object(self.db2.get_titleplan_image_meta(title, version, image))
        return jsonify(meta)

    def get_uuid_object(self, uuid):
        meta = self._make_object(self.db2.get_titleplan_uuid_image_meta(uuid))
        return jsonify(meta)



 
    # ===============

    def get_data(self, uuid):
        image_info = self.db2.get_titleplan_uuid_image_meta(uuid) 
        return self._get_data(image_info )

    def get_data(self, title, document, version, obj_no):
        image_info = self.db2.get_titleplan_image_meta(title, version, obj_no) 
        return self._get_data(image_info )


    def _get_data(self, object_info):
        self.app.logger.debug(object_info)
        title = object_info["TITLE_NO"].strip()
        image = object_info["FP_IMAGE_NO"]
        version = object_info["FP_VERS_NO"]
        _format = object_info['FP_IMAGE_FORMAT']
        adaptor_response = self.db2.get_titleplan_data(title, image, version)
        return self._return_data(adaptor_response, _format)


    # ===============

    def set_uuid(self, title, document, version, image_no):
        meta = self.db2.set_uuid("titleplan", title, document, version, image_no )
        meta = self._make_object(meta)
        return jsonify(meta)

    def set_meta(self, uuid, metadata):
        meta = self.db2.set_meta('titleplan', uuid, metadata)
        return jsonify(self._make_object(meta))