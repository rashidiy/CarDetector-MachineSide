import time
import requests
import config as cfg

from requests.auth import HTTPDigestAuth


class RequestAPI:
    base_link = cfg.SERVER_URL + '/api/cam'
    camera_link = cfg.DAHUA_CAMERA_URL

    security_params = {'camera_id': cfg.CAMERA_ID, 'security_key': cfg.SECURITY_KEY}
    digest_auth = HTTPDigestAuth(cfg.DAHUA_CAMERA_LOGIN, cfg.DAHUA_CAMERA_PASSWORD)

    def get_url(self, path):
        if not path.startswith('/'):
            raise 'Path must start with "/"'
        url = self.base_link + path
        print(url)
        return url

    def get_events_list(self):
        url = self.get_url('/events/')
        return requests.get(url, params=self.security_params).json()

    def delete_event(self, event_id):
        url = self.get_url('/events/%s/' % event_id)
        return requests.delete(url, params=self.security_params)

    def get_records_list(self):
        url = self.get_url('/records/')
        return requests.get(url, params=self.security_params).json()

    def get_record(self, record_id):
        url = self.get_url('/records/%s/' % record_id)
        return requests.get(url, params=self.security_params)

    def update_record(self, record_id, record_id_in_cam):
        url = self.get_url('/records/%s/' % record_id)
        updated_record = requests.get(url, params=self.security_params).json()
        updated_record['recno'] = record_id_in_cam
        response = self.request_to_dahua('update', **updated_record)
        self.record_request_status(record_id, response)

    def delete_record(self, record_id_cam, name):
        params = {"recno": record_id_cam, 'name': name}
        self.request_to_dahua('remove', **params)

    def edited_records_list(self):
        url = self.get_url('/edited_records/')
        return requests.get(url, params=self.security_params).json()

    def delete_edited_record(self, record_id):
        url = self.get_url('/edited_records/%s/' % record_id)
        return requests.delete(url, params=self.security_params)

    def request_to_dahua(self, action, **kwargs):
        url = self.camera_link + '/cgi-bin/recordUpdater.cgi'
        kwargs = {i[0]: i[1] for i in filter(lambda j: j[1] is not None, kwargs.items())}
        params = {
            'action': action,
            **kwargs
        }
        return requests.get(url, params, auth=self.digest_auth)

    def add_record_to_dahua(self, **kwargs):
        response = self.request_to_dahua('insert', **kwargs)
        self.record_request_status(kwargs.get('id'), response)

    def record_request_status(self, record_id, response):
        data = {
            'served_from_server': True,
        }
        if response.status_code == 200:
            if '=' in response.text:
                rec_no = response.text.split('=')[1].strip()
                data['record_id_in_cam'] = rec_no
        else:
            data['is_error'] = True
            data['error_message'] = response.text
        url = self.get_url('/records/%s/' % record_id)
        requests.patch(url, json=data, params=self.security_params)

    def write_new_records(self):
        records_list = self.get_records_list()
        for record in records_list:
            self.add_record_to_dahua(**record)

    def write_changed_records(self):
        updated_record_list = self.edited_records_list()
        for record in updated_record_list:
            type_ = record.get('type')
            record_id = record.get('record_id')
            record_id_cam = record.get('record_id_in_cam')
            name = record.get('name')
            if type_ == 'edited':
                self.update_record(record_id, record_id_cam)
            if type_ == 'deleted':
                self.delete_record(record_id_cam, name)
            self.delete_edited_record(record.get('id'))

    def run(self):
        while True:
            for event in self.get_events_list():
                event_id = event.get('id')
                action = event.get('action')
                match action:
                    case 'new_record':
                        self.write_new_records()
                    case 'updated_record':
                        self.write_changed_records()
                    case 'deleted_record':
                        self.write_changed_records()
                self.delete_event(event_id)
            time.sleep(2)


def main():
    RequestAPI().run()


main()
