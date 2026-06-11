from concurrent import futures
import grpc

import testlab_pb2
import testlab_pb2_grpc

BLACKLIST = ["bad@email.com", "spam@test.com"]


class BlacklistService(testlab_pb2_grpc.BlacklistServiceServicer):

    def CheckBlacklist(self, request, context):
        email = request.email

        if email in BLACKLIST:
            return testlab_pb2.BlacklistResponse(blocked=True)

        return testlab_pb2.BlacklistResponse(blocked=False)


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    testlab_pb2_grpc.add_BlacklistServiceServicer_to_server(
        BlacklistService(),
        server
    )

    server.add_insecure_port("[::]:50052")
    server.start()

    print("Blacklist Service running on 50052")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()