#!/usr/bin/env python3
"""
OpenVAS Connector resorting to the OpenVAS Management Protocol (OMP) 7.0 client.
Official OMP API: http://docs.greenbone.net/API/OMP/omp-7.0.html
"""
try:
    from lxml import etree
except ImportError:
    print('ImportError, using default xml.etree.ElementTree')
    import xml.etree.ElementTree as etree
import shlex
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PRINT_COMMANDS_AND_OUTPUT = False
GET_LAST_COMMAND_OUTPUT = True

# CREATE


def create_alert(name, condition_dict, event_dict, method_dict, comment=None):
    """
    In short: Create an alert.

    The client uses the create_alert command to create a new alert.
    """
    root = etree.Element('create_alert')

    tree_name = etree.SubElement(root, 'name')

    tree_condition = etree.SubElement(root, 'condition')
    if 'data' in condition_dict and 'data_name' in condition_dict:
        tree_condition_data = etree.SubElement(tree_condition, 'data')
        tree_condition_data_name = etree.SubElement(tree_condition_data,
                                                    'name')

    tree_event = etree.SubElement(root, 'event')
    if event_dict['data'] and event_dict['data_name']:
        tree_event_data = etree.SubElement(tree_event, 'data')
        tree_event_data_name = etree.SubElement(tree_event_data, 'name')

    tree_method = etree.SubElement(root, 'method')
    if method_dict['data'] and method_dict['data_name']:
        tree_method_data = etree.SubElement(tree_method, 'data')
        tree_method_data_name = etree.SubElement(tree_method_data, 'name')

    tree_comment = etree.SubElement(root, 'comment')

    tree_name.text = name

    tree_condition.text = condition_dict['condition']
    if 'data' in condition_dict and 'data_name' in condition_dict:
        tree_condition_data.text = condition_dict['data']
        tree_condition_data_name.text = condition_dict['data_name']

    tree_event.text = event_dict['event']
    if event_dict['data'] and event_dict['data_name']:
        tree_event_data.text = event_dict['data']
        tree_event_data_name.text = event_dict['data_name']

    tree_method.text = method_dict['method']
    if method_dict['data'] and method_dict['data_name']:
        tree_method_data.text = method_dict['data']
        tree_method_data_name.text = method_dict['data_name']

    if comment:
        tree_comment.text = comment

    return send_command_xml(root)


def create_target(hosts, name=None, comment=None):
    """ In short: Create a target.

    The client uses the create_target command to create a new target.
    """
    if name is None:
        name = hosts

    root = etree.Element("create_target")
    tree_name = etree.SubElement(root, "name")
    tree_comment = etree.SubElement(root, "comment")
    tree_host = etree.SubElement(root, "hosts")
    tree_name.text = name
    if comment:
        tree_comment.text = comment
    tree_host.text = hosts
    return send_command_xml(root)


def create_task(name,
                target_id,
                config_id="daba56c8-73ec-11df-a475-002264764cea",
                alert_id=None,
                comment=None):
    """ In short: Create a task.

    The client uses the create_task command to create a new task.
    """
    root = etree.Element("create_task")
    tree_name = etree.SubElement(root, "name")
    tree_target = etree.SubElement(root, "target")
    tree_config = etree.SubElement(root, "config")
    tree_alert = etree.SubElement(root, "alert")
    tree_comment = etree.SubElement(root, "comment")

    tree_name.text = name
    tree_target.set("id", target_id)
    tree_config.set("id", config_id)
    if alert_id:
        tree_alert.set("id", alert_id)
    if comment:
        tree_comment.text = comment

    return send_command_xml(root)


# DELETE


def delete_alert(alert_id):
    root = etree.Element("delete_alert")
    root.set('alert_id', alert_id)
    return send_command_xml(root)

def delete_report(report_id):
    root = etree.Element("delete_report")
    root.set('report_id', report_id)
    return send_command_xml(root)

def delete_target(target_id):
    root = etree.Element("delete_target")
    root.set('target_id', target_id)
    return send_command_xml(root)


def delete_task(task_id):
    root = etree.Element("delete_task")
    root.set('task_id', task_id)
    return send_command_xml(root)


# GET


def get_alerts(alert_id=None, filt=None):
    """In short: Get one or many alerts.

    The client uses the get_alerts command to get alert information.
    If the command sent by the client was valid, the connector will
    reply with a list of alerts to the client.
    """
    root = etree.Element("get_alerts")
    if alert_id:
        root.set("alert_id", alert_id)
    if filt:
        root.set("filter", filt)
    return send_command_xml(root)


def get_configs(config_id=None, filt=None):
    """ In short: Get one or many configs.

    The client uses the get_configs command to get config information.
    If the command sent by the client was valid, the connector will reply
    with a list of configs to the client.
    """
    root = etree.Element("get_configs")
    if config_id:
        root.set("config_id", config_id)
    if filt:
        root.set("filter", filt)
    return send_command_xml(root)


def get_port_lists(port_list_id=None, filt=None):
    """ In short: Get one or many port lists.

    The client uses the get_port_lists command to get port list information.
    """
    root = etree.Element("get_port_lists")
    if port_list_id:
        root.set("port_list_id", port_list_id)
    if filt:
        root.set("filter", filt)
    return send_command_xml(root)


def get_reports(report_id=None,
                file_type=None,
                filt=None,
                delta_report_id=None):
    """In short: Get one or many reports.

    The client uses the get_reports command to get report information.

    The XML report format is sent as XML. All other formats are sent in
    Base64 encoding.
    """
    root = etree.Element("get_reports")
    if report_id:
        root.set("report_id", report_id)
    if file_type:
        root.set("format", file_type)
    if filt:
        root.set("filter", filt)
    if delta_report_id:
        try:
            if report_id is None or filt is None or "task_id=" not in filt:
                raise IOError
            root.set("delta_report_id", delta_report_id)
        except IOError:
            print(
                "[Warning] Report ID and Task ID are needed for delta reports."
                "Ignoring delta report ID in the output.")

    return send_command_xml(root)


def get_results(result_id=None, filt=None):
    """In short: Get results.

    The client uses the get_results command to get result information.

    If the request includes a notes flag, an overrides flag or an
    apply_overrides flag and any of these is true, then the request must
    also include a task ID.
    """
    root = etree.Element("get_results")
    if result_id:
        root.set("result_id", result_id)
    if filt:
        root.set("filter", filt)
    return send_command_xml(root)


def get_targets(result_id=None, filt=None):
    """In short: Get one or many targets.

    The client uses the get_targets command to get target information.
    """
    root = etree.Element("get_targets")
    if result_id:
        root.set("result_id", result_id)
    if filt:
        root.set("filter", filt)
    return send_command_xml(root)


def get_tasks(task_id=None, filt=None):
    """In short: Get one or many tasks.

    The client uses the get_tasks command to get task information.

    As a convenience for clients the response includes a task count and the
    values of the sort order, sort field and apply overrides flag that the
    connector applied when selecting the tasks.
    """
    root = etree.Element("get_tasks")
    if task_id:
        root.set("task_id", task_id)
    if filt:
        root.set("filter", filt)
    return send_command_xml(root)


# RUN


def start_task(task_id):
    """In short: Manually start an existing task.

    The client uses the start_task command to manually start an existing task.
    """
    root = etree.Element("start_task", task_id=task_id)
    return send_command_xml(root)


def stop_task(task_id):
    """In short: Stop a running task.

    The client uses the stop_task command to manually stop a running task.
    """
    root = etree.Element("stop_task", task_id=task_id)
    return send_command_xml(root)


# Aux Functions
def send_command_xml(xml_cmd):
    """ Executes an OMP command with the XML object received """
    cmd = 'omp --pretty-print --xml=\'' + etree.tostring(
        xml_cmd, encoding="unicode") + '\''
    xml_string = subprocess.check_output(shlex.split(cmd))
    if PRINT_COMMANDS_AND_OUTPUT:
        print(cmd)
        print(prettify_xml_string(xml_string))
    if GET_LAST_COMMAND_OUTPUT:
        text_file = open("log.xml", "w")
        text_file.write("<!--" + cmd + "-->\n")
        text_file.write(prettify_xml_string(xml_string))
        text_file.close()
    return etree.fromstring(xml_string)


def prettify_xml_string(xml_string):
    """ Formats xml string into a pretty print xml string
    """
    # pylint: disable=E1123
    return etree.tostring(
        etree.fromstring(xml_string), encoding="unicode", pretty_print=True)


# Advanced Functions


def wait_for_http_alert(host='127.0.0.1', port='8081', get_method=''):
    """ Waits for a HTTP GET request until the alert from OpenVAS is activated.
    It locks the current thread while waiting.
    """

    class ReceiveAlertHandler(BaseHTTPRequestHandler):
        """ HTTP Server, ends when GET request with 'get_method' is received.
        """

        def do_GET(self):
            """ GET Method
            """
            if self.path.endswith(get_method):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = 'Alert received. Task completed.'
                # Write content as utf-8 data
                self.wfile.write(bytes(message, "utf8"))
                print(message)
                # return response and shutdown the server
                import threading
                threading.Thread(
                    target=self.server.shutdown, daemon=True).start()

        def log_message(self, message_format, *args):
            ''' avoids spam from openvas's NVTs '''
            return

    print('Waiting for HTTP GET in: ' + host + ':' + str(port) + get_method)
    server_address = (host, port)
    httpd = HTTPServer(server_address, ReceiveAlertHandler)
    httpd.serve_forever()


def create_http_alert(name, status='Done', url='http://127.0.0.1:8081'):
    """ Create alert to send HTTP Get request when status changes.
    """
    condition_dict = {'condition': 'Always'}
    event_dict = {
        'event': 'Task run status changed',
        'data': 'Requested',
        'data_name': 'status'
    }
    method_dict = {'method': 'HTTP Get', 'data_name': 'URL'}

    event_dict['data'] = status
    method_dict['data'] = url + '/task_done'

    return create_alert(name, condition_dict, event_dict, method_dict)


@DeprecationWarning
def get_report_when_done(task_id, status_timer=3600):
    ''' Gets a report when task is done if no previous report exists
    else compares both reports (delta report)
    '''
    while True:
        get_tasks_response = get_tasks(task_id)
        status = get_tasks_response.xpath(
            '/get_tasks_response/task/status/text()')[0]
        if status == 'Done':
            print('Task finished')
            break
        progress = int(
            get_tasks_response.xpath(
                '/get_tasks_response/task/progress/text()')[0])
        time_to_sleep = status_timer * 0.2 + status_timer * 0.8 * (
            1 - progress / 100)
        print('Task in progress ([' + status + '] ' + str(progress) +
              '%). Checking again in ' + str(time_to_sleep) + ' seconds.')
        time.sleep(time_to_sleep)
    return get_last_reports(task_id)


def get_last_reports(task_id):
    """ Gets 2 last reports, if there is only one report it outputs the
    regular get_reports command else it compares (delta report) the 2 last
    reports.
    """
    get_tasks_response = get_tasks(task_id)
    last_report_id = get_tasks_response.xpath(
        '/get_tasks_response/task/last_report/report/@id')[0]
    report_count = int(
        get_tasks_response.xpath(
            '/get_tasks_response/task/report_count/finished/text()')[0])
    filter_task = "task_id=" + task_id + " rows=1000"
    if report_count > 1:
        second_last_report_id = get_tasks_response.xpath(
            '/get_tasks_response/task/second_last_report/report/@id')[0]
        # returns changes in last report
        return get_reports(
            second_last_report_id,
            filt=filter_task,
            delta_report_id=last_report_id)
    return get_reports(last_report_id, filt=filter_task)
