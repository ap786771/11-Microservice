#!/usr/bin/python
#
# Copyright 2018 Google LLC
# Licensed under the Apache License, Version 2.0
#
# Author: Abhishek Pandey (modified)

import grpc
import demo_pb2
import demo_pb2_grpc

from logger import getJSONLogger
logger = getJSONLogger('emailservice-client')

def send_confirmation_email(email, order):
    channel = grpc.insecure_channel('[::]:8080')   # gRPC service running on 8080
    stub = demo_pb2_grpc.EmailServiceStub(channel)
    try:
        response = stub.SendOrderConfirmation(
            demo_pb2.SendOrderConfirmationRequest(
                email=email,
                order=order
            )
        )
        logger.info('Request sent successfully.')
        return response
    except grpc.RpcError as err:
        logger.error(err.details())
        logger.error('{}, {}'.format(err.code().name, err.code().value))

if __name__ == '__main__':
    logger.info('Client for email service.')
    send_confirmation_email(
        "abhishekpandey18362@gmail.com",
        "Your order is complete! Confirmation #04c855ea, Tracking #AD-37028-188890567, Total Paid $27.98"
    )
