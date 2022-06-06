# must be called as we're using zipped requirements
try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    import json
    import logging
    from logging import StreamHandler
    from datadog_api_client.v2 import ApiClient, ApiException, Configuration
    from datadog_api_client.v2.api import logs_api
    from datadog_api_client.v2.models import *
except Exception as e:
    print("Error : {} ".format(e))


class DDHandler(StreamHandler):
    def __init__(self, configuration, service_name, ddsource):
        StreamHandler.__init__(self)
        self.configuration = configuration
        self.service_name = service_name
        self.ddsource = ddsource

    def emit(self, record):
        msg = self.format(record)

        with ApiClient(self.configuration) as api_client:
            api_instance = logs_api.LogsApi(api_client)
            body = HTTPLog(
                [
                    HTTPLogItem(
                        ddsource=self.ddsource,
                        ddtags="env:{}".format(
                            os.getenv("ENV"),

                        ),
                        message=msg,
                        service=self.service_name,
                    ),
                ]
            )

            try:
                # Send logs
                api_response = api_instance.submit_log(body)
            except ApiException as e:
                print("Exception when calling LogsApi->submit_log: %s\n" % e)


class Logging(object):
    def __init__(self, service_name, ddsource, logger_name='demoapp'):

        self.service_name = service_name
        self.ddsource = ddsource
        self.logger_name = logger_name


        self.configuration = Configuration()
        format = "[%(asctime)s] %(name)s %(levelname)s %(message)s"
        self.logger = logging.getLogger(self.logger_name)
        formatter = logging.Formatter(
            format,
        )


        # Logs to Datadog
        dd = DDHandler(self.configuration, service_name=self.service_name,ddsource=self.ddsource)
        dd.setLevel(logging.INFO)
        dd.setFormatter(formatter)
        self.logger.addHandler(dd)

        if logging.getLogger().hasHandlers():
            logging.getLogger().setLevel(logging.INFO)
        else:
            logging.basicConfig(level=logging.INFO)


def handler(event, context):

    logger = Logging(service_name='lambda', ddsource='source1', logger_name='DemoApp')
    response = {
        "statusCode": 200,
        "body": json.dumps("Hello From Lambda")
    }

    logger.logger.info(response)

