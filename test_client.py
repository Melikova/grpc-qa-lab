import grpc
import testlab_pb2
import testlab_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50052")
    stub = testlab_pb2_grpc.BlacklistServiceStub(channel)

    emails = ["bad@email.com", "good@email.com"]

    for email in emails:
        response = stub.CheckBlacklist(
            testlab_pb2.BlacklistRequest(email=email)
        )
        print(email, "→", response.blocked)

if __name__ == "__main__":
    run()

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = testlab_pb2_grpc.UserServiceStub(channel)

    emails = ["bad@email.com", "good@email.com"]

    for email in emails:
        response = stub.GetUser(
            testlab_pb2.UserRequest(email=email)
        )

        print(email, "→", response.status)


if __name__ == "__main__":
    run()