# -*- coding: utf-8 -*-
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import time
from  time import sleep
from posixpath import join as posixjoin
from urllib.parse import quote

from docs_documents_api.exceptions import   ApplicationError
 
class Db2:

    def reset_session(self):
        self.app.logger.debug("reset connection")

        try:
            self.session.close()
            del self.session
        except Exception as e:
            pass
        sleep(0.1) # give some time
        self.session = requests.Session() # create a session to keep a TCP connection open

        self.app.logger.debug("connection reset")


    def __init__(self, app, url, key, **kwargs):
        self.app = app
        self.key = key
        self.url = url
        self.timeout = kwargs.get("timeout", 60)
        self.retries = kwargs.get("retries", 1)
        self.reset_session()
        self.headers = {'Content-Type': 'application/json',
                        'X-Api-Key': key}
        if kwargs.get('ignore_cert',False):
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


    # TODO need to look at ssl verification in request call
    def request(self, method, url, params=None, data=None, raw_response=False, timeout=None):
        kwargs = dict({}, **{
            'headers': self.headers,
            'params': params or {}
        })
 
        if method in ('post', 'put', 'delete'):
            kwargs['data'] = json.dumps(data)
            kwargs['headers']['Content-Type'] = 'application/json'


        # this retry loop assumes that all requests are idempotent and so we can retry on fail
        retries = 0
        while True:
            try:
                if retries > 0:
                    sleep(0.01)  # reset thread scheduling 0.0001?
                if timeout == None:
                    timeout = self.timeout
                response = getattr(self.session, method)(url, timeout=timeout, verify=False, **kwargs)
                break
            except Exception as e:
                self.app.logger.debug("retrying {0} {1} {2}".format(retries, method, url))
                self.reset_session()
                retries = retries + 1
                if retries >= self.retries:
                    # the underlying libraries should normally automatically re-establish a connection
                    # this is to deal with a situation where ES has hung
                    self.reset_session()
                if retries > self.retries:
                    self.app.logger.debug('Max number of retries exceeded')
                    raise e

        if response.status_code in [200, 201]:
            if 'Content-Type' in response.headers:
                if 'image' in response.headers['Content-Type']: 
                    return response   
                if 'application/octet-stream' in response.headers['Content-Type']:
                    return response         
            try:
                return response.json()
            except (ValueError, TypeError):
                response.encoding = "UTF-8"  
                return response.text
        elif response.status_code in [404]:
            raise ApplicationError(response.text,'NOTFOUND', 404, True)   
        elif response.status_code in [400]:
            raise ApplicationError(response.text,'BADREQUEST', 400, True)         
        elif response.status_code in [403]:
            raise ApplicationError(response.text,'FORBIDDEN', 403, True) 
        else:
            self.app.logger.debug('Link Error {}'.format(response.text))
            raise ApplicationError(response.text,'LINKERROR', 500, True)



# helper
    def make_url(self, *args):
        url = posixjoin(self.url, *args)
        return url

# 
    def health(self):
        self.app.logger.debug('get health')
        
        health = {}
        try:
            url = self.make_url("health")
            health["status"] = self.request("get", url) 
            health["health"] = "alive"
        except:
            health["health"] = "dead"
        self.app.logger.debug(health)    
        return health


    def get_titles(self, doc_type, start, size):
        url = self.make_url(doc_type, "titles")
        params = {}
        if start is not None:
            params['start'] = start
        if size is not None:
            params['size'] = size    
        result = self.request("get", url, params = params)
        return result

    def get_documents(self, doc_type, title_no, start, size):
        self.app.logger.debug('get document list')
        result = {}
        url = self.make_url(doc_type,"titles", title_no, "documents")
        params = {}
        if start is not None:
            params['start'] = start
        if size is not None:
            params['size'] = size    
        result = self.request("get", url,  params = params) 
        return result

    def get_document_meta(self, doc_type, title_no, doc_no):
        self.app.logger.debug('get document meta {} {}'.format(title_no, doc_no))  
        result = {}
        url = self.make_url( doc_type , "titles", title_no, "documents", doc_no)
        result = self.request("get", url) 
        return result

    def get_objects_in_state(self, doc_type, state, size = '10'):
        url = self.make_url(doc_type, "objects")
        return self.request("get", url, params = {'state': state, 'size': size })

    def set_uuid(self, doc_type, title_no, doc_no, version_no, object_no):   
        if doc_type == 'titleplan':
            url = self.make_url(doc_type,"titles",title_no,"versions",version_no,"images",object_no,"_uuid")
            result = self.request("put",url)
            return result
        else:
            pass

    def set_meta(self, doc_type, uuid, metadata):   
        if doc_type == 'titleplan':
            url = self.make_url(doc_type, "uuids", uuid)
            result = self.request("put", url, data=metadata)
            return result
        else:
            pass



    def get_retained_page_meta(self, title_no, doc_no, page_no):
        self.app.logger.debug('get document {}'.format(doc_no))  
        result = {}
 
        url = self.make_url( "retained", "titles", title_no, "documents", doc_no, "objects", page_no)
        result = self.request("get", url) 
        return result

    def get_retained_data(self, title_no, doc_no, page_no):
        self.app.logger.debug('get referred document: for title {} deed no: {} page no: {}'.format(title_no, doc_no, page_no));
        
        url = self.make_url("retained", "data", title_no, doc_no, page_no)
        result = self.request("get", url) 
        return result

    def get_retained_uuid(self, uuid):
        self.app.logger.debug('get titleplan for uuid: {}'.format(uuid))
        
        url = self.make_url("retained", "uuids", uuid)
        result = self.request("get", url)
   
        return result


    def get_titleplan_images_meta(self, title_no, version_no):
        url = self.make_url( "titleplan", "titles", title_no, "versions", version_no, "images")
        result = self.request("get", url)
        return result


    def get_retained_pages(self, title_no, doc_no):
        self.app.logger.debug('get document {}'.format(doc_no)) 
        url = self.make_url("retained" , "titles", title_no, "documents", doc_no, "objects")
        result = self.request("get", url) 
        return result


    def get_titleplan_versions(self, title_no):
        url = self.make_url( "titleplan", "titles", title_no, "versions")
        result = self.request("get", url)
        return result

    def get_titleplan_image_meta(self, title_no, version_no, image_no):
        self.app.logger.debug('get titleplan for title: {} flap no: {} version no: {}'.format(title_no, image_no, version_no))
        url = self.make_url("titleplan", "titles", title_no, "versions", version_no, "images", image_no)
        result = self.request("get", url)
        return result

    def get_titleplan_uuid_image_meta(self, uuid):
        self.app.logger.debug('get titleplan for uuid: {}'.format(uuid));
        url = self.make_url("titleplan", "uuids", uuid)
        result = self.request("get", url)
        return result

    def get_titleplan_data(self, title_no, image_no, version_no):
        self.app.logger.debug('get titleplan image for title: {} flap no: {} version no: {}'.format(title_no, image_no, version_no));
        
        url = self.make_url("titleplan", "data", title_no, version_no, image_no)
        result = self.request("get", url)
   
        return result

    