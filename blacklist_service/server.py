import signal
import logging
from concurrent import futures

import grpc
import testlab_pb2
import testlab_pb2_grpc


# ── Logging ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("BlacklistService")


# ── Blacklist dataset ──────────────────────────────────────────────────────────

BLACKLIST = {"bad@email.com", "spam@test.com"}  # set → O(1) lookup vs list O(n)


# ── Service implementation ─────────────────────────────────────────────────────

class BlacklistService(testlab_pb2_grpc.BlacklistServiceServicer):

    def CheckBlacklist(self, request, context):
        logger.info("CheckBlacklist called | email=%r", request.email)

        # Validate: email must not be empty
        if not request.email:
            logger.warning("Empty email field received")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("email field is required")
            return testlab_pb2.BlacklistResponse()

        is_blocked = request.email in BLACKLIST
        logger.info("Result | email=%r blocked=%s", request.email, is_blocked)

        return testlab_pb2.BlacklistResponse(blocked=is_blocked)


# ── Server setup ───────────────────────────────────────────────────────────────

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    testlab_pb2_grpc.add_BlacklistServiceServicer_to_server(
        BlacklistService(),
        server,
    )

    server.add_insecure_port("[::]:50052")
    server.start()

    logger.info("BlacklistService running on port 50052")

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