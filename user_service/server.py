import signal
import logging
from concurrent import futures

import grpc
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import testlab_pb2
import testlab_pb2_grpc


# ── Logging ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("UserService")


# ── Service implementation ─────────────────────────────────────────────────────

class UserService(testlab_pb2_grpc.UserServiceServicer):

    def __init__(self):
        # Channel created once and reused — don't open a new channel per request
        channel = grpc.insecure_channel("localhost:50052")
        self.blacklist_stub = testlab_pb2_grpc.BlacklistServiceStub(channel)
        logger.info("Connected to BlacklistService on localhost:50052")

    def GetUser(self, request, context):
        logger.info("GetUser called | email=%r", request.email)

        # Validate: email must not be empty
        if not request.email:
            logger.warning("Empty email field received")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("email field is required")
            return testlab_pb2.UserResponse()

        # Call BlacklistService — handle downstream failure gracefully
        try:
            blacklist_response = self.blacklist_stub.CheckBlacklist(
                testlab_pb2.BlacklistRequest(email=request.email),
                timeout=3,  # don't wait forever if BlacklistService is down
            )
        except grpc.RpcError as e:
            logger.error(
                "BlacklistService call failed | code=%s details=%s",
                e.code(), e.details(),
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("upstream blacklist check failed")
            return testlab_pb2.UserResponse()

        status = testlab_pb2.UserStatus.Value(
            "USER_STATUS_BLOCKED" if blacklist_response.blocked else "USER_STATUS_ACTIVE"
        )

        logger.info(
            "GetUser result | email=%r blocked=%s",
            request.email, blacklist_response.blocked,
        )

        return testlab_pb2.UserResponse(
            email=request.email,
            status=status,
        )


# ── Server setup ───────────────────────────────────────────────────────────────

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    testlab_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(),
        server,
    )

    server.add_insecure_port("[::]:50051")
    server.start()

    logger.info("UserService running on port 50051")

    # Graceful shutdown on SIGTERM / SIGINT (Ctrl+C)
    def shutdown(signum, frame):
        logger.info("Shutdown signal received — stopping server (grace=5s)")
        server.stop(grace=5)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    server.wait_for_termination()
    logger.info("Server stopped")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    serve()