#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
#

from concurrent import futures
import os
import time
import grpc
import traceback
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
    TemplateError
)

import demo_pb2
import demo_pb2_grpc

from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from opentelemetry import trace
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorServer
)

from opentelemetry.sdk.trace import (
    TracerProvider
)

from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)

from google.auth.exceptions import (
    DefaultCredentialsError
)

import googlecloudprofiler

from logger import getJSONLogger

logger = getJSONLogger('emailservice-server')

# ============================================================
# Load Email Template
# ============================================================

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('confirmation.html')

# ============================================================
# Base Service
# ============================================================

class BaseEmailService(
    demo_pb2_grpc.EmailServiceServicer
):

    def Check(self, request, context):

        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )

    def Watch(self, request, context):

        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED
        )

# ============================================================
# REAL EMAIL SERVICE
# ============================================================

class DummyEmailService(BaseEmailService):

    def SendOrderConfirmation(
        self,
        request,
        context
    ):

        receiver_email = request.email

        logger.info(
            'A request to send order confirmation email to {} has been received.'.format(
                receiver_email
            )
        )

        # ====================================================
        # Gmail SMTP Configuration
        # ====================================================

        sender_email = "abhishekpandey18362@gmail.com"

        sender_password = "abhimanyu@034912"

        subject = "Order Confirmation"

        # ====================================================
        # Render HTML Template
        # ====================================================

        try:

            confirmation = template.render(
                order=request.order
            )

        except TemplateError as err:

            logger.error(
                "Template rendering failed: {}".format(
                    str(err)
                )
            )

            context.set_code(
                grpc.StatusCode.INTERNAL
            )

            context.set_details(
                "Template rendering failed"
            )

            return demo_pb2.Empty()

        # ====================================================
        # Create Email
        # ====================================================

        msg = MIMEMultipart()

        msg["From"] = sender_email

        msg["To"] = receiver_email

        msg["Subject"] = subject

        msg.attach(
            MIMEText(
                confirmation,
                "html"
            )
        )

        # ====================================================
        # Send Email
        # ====================================================

        try:

            server = smtplib.SMTP(
                "smtp.gmail.com",
                587
            )

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.sendmail(
                sender_email,
                receiver_email,
                msg.as_string()
            )

            server.quit()

            logger.info(
                "Email sent successfully to {}".format(
                    receiver_email
                )
            )

        except Exception as e:

            logger.error(
                "Failed to send email: {}".format(
                    str(e)
                )
            )

            context.set_code(
                grpc.StatusCode.INTERNAL
            )

            context.set_details(
                "Email sending failed"
            )

            return demo_pb2.Empty()

        return demo_pb2.Empty()

# ============================================================
# Health Check
# ============================================================

class HealthCheck():

    def Check(self, request, context):

        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )

# ============================================================
# Start Server
# ============================================================

def start(dummy_mode):

    server = grpc.server(
        futures.ThreadPoolExecutor(
            max_workers=10
        ),
    )

    service = None

    if dummy_mode:

        service = DummyEmailService()

    else:

        raise Exception(
            'non-dummy mode not implemented yet'
        )

    demo_pb2_grpc.add_EmailServiceServicer_to_server(
        service,
        server
    )

    health_pb2_grpc.add_HealthServicer_to_server(
        service,
        server
    )

    port = os.environ.get(
        'PORT',
        "8080"
    )

    logger.info(
        "listening on port: " + port
    )

    server.add_insecure_port(
        '[::]:' + port
    )

    server.start()

    try:

        while True:

            time.sleep(3600)

    except KeyboardInterrupt:

        server.stop(0)

# ============================================================
# Profiler
# ============================================================

def initStackdriverProfiling():

    project_id = None

    try:

        project_id = os.environ[
            "GCP_PROJECT_ID"
        ]

    except KeyError:

        pass

    for retry in range(1, 4):

        try:

            if project_id:

                googlecloudprofiler.start(
                    service='email_server',
                    service_version='1.0.0',
                    verbose=0,
                    project_id=project_id
                )

            else:

                googlecloudprofiler.start(
                    service='email_server',
                    service_version='1.0.0',
                    verbose=0
                )

            logger.info(
                "Successfully started Stackdriver Profiler."
            )

            return

        except (BaseException) as exc:

            logger.info(
                "Unable to start Stackdriver Profiler Python agent. "
                + str(exc)
            )

            if retry < 4:

                logger.info(
                    "Sleeping %d to retry initializing Stackdriver Profiler"
                    % (retry * 10)
                )

                time.sleep(1)

            else:

                logger.warning(
                    "Could not initialize Stackdriver Profiler after retrying"
                )

    return

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':

    logger.info(
        'starting the email service in dummy mode.'
    )

    # ========================================================
    # Profiler
    # ========================================================

    try:

        if "DISABLE_PROFILER" in os.environ:

            raise KeyError()

        else:

            logger.info(
                "Profiler enabled."
            )

            initStackdriverProfiling()

    except KeyError:

        logger.info(
            "Profiler disabled."
        )

    # ========================================================
    # Tracing
    # ========================================================

    try:

        if os.environ["ENABLE_TRACING"] == "1":

            otel_endpoint = os.getenv(
                "COLLECTOR_SERVICE_ADDR",
                "localhost:4317"
            )

            trace.set_tracer_provider(
                TracerProvider()
            )

            trace.get_tracer_provider().add_span_processor(

                BatchSpanProcessor(

                    OTLPSpanExporter(
                        endpoint=otel_endpoint,
                        insecure=True
                    )
                )
            )

        grpc_server_instrumentor = (
            GrpcInstrumentorServer()
        )

        grpc_server_instrumentor.instrument()

    except (
        KeyError,
        DefaultCredentialsError
    ):

        logger.info(
            "Tracing disabled."
        )

    except Exception as e:

        logger.warning(
            f"Exception on Cloud Trace setup: {traceback.format_exc()}, tracing disabled."
        )

    # ========================================================
    # Start Server
    # ========================================================

    start(dummy_mode=True)
