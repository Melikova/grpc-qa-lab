# Mini gRPC QA Playground

## Purpose

Build a lightweight gRPC-based microservice application to demonstrate understanding of:

- gRPC communication
- Protocol Buffers (Protobuf)
- Service-to-service communication
- API testing using Postman and grpcurl
- QA testing strategies for distributed systems

---

## Services

### 1. User Service

**Responsibilities:**

- Receive user requests containing an email address
- Call Blacklist Service via gRPC
- Process the response
- Return the user's status

### 2. Blacklist Service

**Responsibilities:**

- Receive email validation requests
- Check whether the email exists in the blacklist
- Return the blacklist status

---

## System Flow

```text
Client (Postman / grpcurl)
        ↓
User Service (gRPC Server)
        ↓
Blacklist Service (gRPC Server)
        ↓
Returns blacklist result
        ↓
User Service returns final user status
```

---

## Functional Requirements

### User Service

- Accept an email address as input
- Call Blacklist Service using gRPC
- Return one of the following statuses:
  - ACTIVE
  - BLOCKED

### Blacklist Service

- Accept an email address as input
- Check the email against an internal blacklist
- Return:

```json
{
  "blocked": true
}
```

or

```json
{
  "blocked": false
}
```

---

## Non-Functional Requirements

- Use gRPC as the communication protocol
- Use HTTP/2 transport
- Use Protocol Buffers for message serialization
- Run entirely in a local environment
- Target response time below 50 ms
- Services must remain stateless

---

## Test Scenarios

### Functional Testing

- Valid email returns ACTIVE
- Blacklisted email returns BLOCKED

### Negative Testing

- Empty email
- Missing email field
- Invalid email format

### Integration Testing

- Verify User Service successfully calls Blacklist Service
- Verify correct data mapping between services
- Verify correct final status is returned to the client

---

## Technology Stack

- Python
- gRPC
- Protocol Buffers (.proto)
- Postman
- grpcurl

---

## Project Scope

- Unary gRPC calls
- Service-to-service communication
- Basic business logic
- API testing

---

## Sample Response

```json
{
  "email": "john@test.com",
  "status": "ACTIVE"
}
```
