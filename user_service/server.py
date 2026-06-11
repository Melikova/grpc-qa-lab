import grpc
from concurrent import futures

import testlab_pb2
import testlab_pb2_grpc


class UserService(testlab_pb2_grpc.UserServiceServicer):

    def __init__(self):
        channel = grpc.insecure_channel("localhost:50052")
        self.blacklist_stub = testlab_pb2_grpc.BlacklistServiceStub(channel)

    def GetUser(self, request, context):
        email = request.email

        blacklist_response = self.blacklist_stub.CheckBlacklist(
            testlab_pb2.BlacklistRequest(email=email)
        )

        if blacklist_response.blocked:
            return testlab_pb2.UserResponse(
                email=email,
                status="BLOCKED"
            )

        return testlab_pb2.UserResponse(
            email=email,
            status="ACTIVE"
        )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    testlab_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(),
        server
    )

    server.add_insecure_port("[::]:50051")
    server.start()

    print("User Service running on 50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()