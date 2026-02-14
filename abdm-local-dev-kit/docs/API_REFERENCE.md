# ABDM API Reference

Comprehensive reference for all ABDM APIs including endpoints, authentication, and usage patterns.

## Table of Contents

- [Authentication](#authentication)
- [API Architecture](#api-architecture)
- [Core Services](#core-services)
- [Health Information Exchange](#health-information-exchange)
- [Registry Services](#registry-services)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Authentication

### Session Creation

All ABDM APIs require a session token obtained via Client ID and Secret.

**Endpoint**: `POST https://dev.abdm.gov.in/gateway/v0.5/sessions`

**Request**:
```json
{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret"
}
```

**Response**:
```json
{
  "accessToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 600,
  "refreshToken": "refresh-token-string",
  "refreshExpiresIn": 1800,
  "tokenType": "bearer"
}
```

**Usage**: Include in all subsequent requests:
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Required Headers

All ABDM API calls must include:

```http
Authorization: Bearer {token}
X-CM-ID: sbx  # 'sbx' for sandbox, 'abdm' for production
X-HIP-ID: {facility-id}  # For HIP requests
X-HIU-ID: {requester-id}  # For HIU requests
Content-Type: application/json
```

## API Architecture

### Asynchronous Pattern

ABDM uses an asynchronous callback model:

1. **Client calls API** → Gateway responds with `202 Accepted`
2. **Gateway processes request** → Invokes registered callback URL
3. **Client callback endpoint** → Receives response and sends `200 OK`

**Example Flow**:

```
Client → POST /v0.5/users/auth/fetch-modes
         ← 202 Accepted {"requestId": "abc123"}

Gateway → POST https://your-callback-url/v0.5/users/auth/on-fetch-modes
          {"requestId": "abc123", "modes": [...]}
Client  ← 200 OK
```

### Callback URL Registration

**Sandbox**:
```http
PATCH https://dev.abdm.gov.in/devservice/v1/bridges
Authorization: Bearer {token}

{
  "url": "https://your-callback-url.com"
}
```

**Verify Registration**:
```http
GET https://dev.abdm.gov.in/devservice/v1/bridge/getServices
Authorization: Bearer {token}
```

**Production**: Register via Health Facility Registry (HFR)

## Core Services

### ABHA Number Service

Create and manage Ayushman Bharat Health Account numbers.

#### Create ABHA via Mobile OTP

**Endpoint**: `POST /v2/registration/aadhaar/generateOtp`

**Request**:
```json
{
  "aadhaar": "123456789012"
}
```

**Response** (async callback):
```json
{
  "txnId": "TXN-abc-123",
  "message": "OTP sent successfully"
}
```

#### Verify OTP and Create ABHA

**Endpoint**: `POST /v2/registration/aadhaar/verifyOtp`

**Request**:
```json
{
  "otp": "123456",
  "txnId": "TXN-abc-123"
}
```

**Response**:
```json
{
  "healthIdNumber": "22-7225-4829-5255",
  "healthId": "username@abdm",
  "name": "John Doe",
  "gender": "M",
  "yearOfBirth": "1990",
  "mobile": "9876543210",
  "token": "user-auth-token"
}
```

### Consent Manager APIs

Manage patient consent for health information access.

#### Request Consent

**Endpoint**: `POST /v0.5/consent-requests/init`

**Request**:
```json
{
  "requestId": "5f7a2668-7a8c-4c5d-a0c6-7b3c9f6d8e1a",
  "timestamp": "2024-03-01T10:30:00.000Z",
  "consent": {
    "purpose": {
      "text": "Care Management",
      "code": "CAREMGT",
      "refUri": "http://terminology.hl7.org/ValueSet/v3-PurposeOfUse"
    },
    "patient": {
      "id": "username@sbx"
    },
    "hiu": {
      "id": "HIU-001"
    },
    "requester": {
      "name": "Dr. Jane Smith",
      "identifier": {
        "type": "REGNO",
        "value": "MH1234",
        "system": "https://doctor.ndhm.gov.in"
      }
    },
    "hiTypes": ["Prescription", "DiagnosticReport"],
    "permission": {
      "accessMode": "VIEW",
      "dateRange": {
        "from": "2023-01-01T00:00:00.000Z",
        "to": "2024-03-01T23:59:59.000Z"
      },
      "dataEraseAt": "2024-04-01T00:00:00.000Z",
      "frequency": {
        "unit": "HOUR",
        "value": 1,
        "repeats": 0
      }
    }
  }
}
```

**Callback**: `/v0.5/consent-requests/on-init`

```json
{
  "requestId": "5f7a2668-7a8c-4c5d-a0c6-7b3c9f6d8e1a",
  "timestamp": "2024-03-01T10:30:05.000Z",
  "consentRequest": {
    "id": "consent-req-123"
  },
  "resp": {
    "requestId": "5f7a2668-7a8c-4c5d-a0c6-7b3c9f6d8e1a"
  }
}
```

#### Fetch Consent Artefact

**Endpoint**: `POST /v0.5/consents/fetch`

**Request**:
```json
{
  "requestId": "7e8b3669-8b9d-5d6e-b1d7-8c4d0g7e9f2b",
  "timestamp": "2024-03-01T11:00:00.000Z",
  "consentId": "consent-123-456-789"
}
```

**Callback**: `/v0.5/consents/on-fetch`

Returns complete consent artefact with permissions and care contexts.

## Health Information Exchange

### Patient Discovery (HIP)

Discover patient records at a facility.

**Callback Endpoint** (implemented by HIP): `POST /v0.5/care-contexts/discover`

**Request from Gateway**:
```json
{
  "requestId": "discovery-req-001",
  "timestamp": "2024-03-01T12:00:00.000Z",
  "transactionId": "txn-discovery-001",
  "patient": {
    "id": "username@sbx",
    "verifiedIdentifiers": [
      {
        "type": "MR",
        "value": "MRN123456"
      }
    ],
    "name": "John Doe",
    "gender": "M",
    "yearOfBirth": "1990"
  }
}
```

**Response to Gateway**: `POST /v0.5/care-contexts/on-discover`

```json
{
  "requestId": "discovery-req-001",
  "timestamp": "2024-03-01T12:00:05.000Z",
  "transactionId": "txn-discovery-001",
  "patient": {
    "referenceNumber": "PAT-001",
    "display": "John Doe",
    "careContexts": [
      {
        "referenceNumber": "VISIT-2024-001",
        "display": "Consultation - 2024-03-01"
      },
      {
        "referenceNumber": "LAB-2024-002",
        "display": "Blood Test - 2024-02-15"
      }
    ],
    "matchedBy": ["MR"]
  },
  "resp": {
    "requestId": "discovery-req-001"
  }
}
```

### Link Care Contexts

**Callback Endpoint**: `POST /v0.5/links/link/init`

**Request**:
```json
{
  "requestId": "link-req-001",
  "timestamp": "2024-03-01T12:05:00.000Z",
  "transactionId": "txn-link-001",
  "patient": {
    "referenceNumber": "PAT-001",
    "display": "John Doe",
    "careContexts": [
      {
        "referenceNumber": "VISIT-2024-001"
      }
    ]
  }
}
```

**Response**: `POST /v0.5/links/link/on-init`

```json
{
  "requestId": "link-req-001",
  "timestamp": "2024-03-01T12:05:05.000Z",
  "transactionId": "txn-link-001",
  "link": {
    "referenceNumber": "LINK-001",
    "authenticationType": "DIRECT",
    "meta": {
      "communicationMedium": "MOBILE",
      "communicationHint": "9876543210",
      "communicationExpiry": "2024-03-01T12:10:00.000Z"
    }
  },
  "resp": {
    "requestId": "link-req-001"
  }
}
```

### Health Information Request (HIU)

Request health data after consent approval.

**Endpoint**: `POST /v0.5/health-information/cm/request`

**Request**:
```json
{
  "requestId": "data-req-001",
  "timestamp": "2024-03-01T13:00:00.000Z",
  "hiRequest": {
    "consent": {
      "id": "consent-123-456-789"
    },
    "dateRange": {
      "from": "2023-01-01T00:00:00.000Z",
      "to": "2024-03-01T23:59:59.000Z"
    },
    "dataPushUrl": "https://hiu-callback-url/data/push",
    "keyMaterial": {
      "cryptoAlg": "ECDH",
      "curve": "Curve25519",
      "dhPublicKey": {
        "expiry": "2024-03-01T14:00:00.000Z",
        "parameters": "Curve25519/32byte random key",
        "keyValue": "base64-encoded-public-key"
      },
      "nonce": "random-nonce-value"
    }
  }
}
```

**Data Push Callback**: `POST {dataPushUrl}`

Encrypted FHIR bundles delivered to HIU's registered callback.

## Registry Services

### Health Facility Registry (HFR)

**Base URL**: https://facility.abdm.gov.in/

#### Search Facility

**Endpoint**: `GET /api/v1/bridges?active=true&offset=0&limit=20`

**Response**:
```json
{
  "bridges": [
    {
      "id": "HFR-001",
      "name": "City Hospital",
      "type": "HIP",
      "active": true
    }
  ]
}
```

### Healthcare Professional Registry (HPR)

**Base URL**: https://hpr.abdm.gov.in/

#### Verify Professional

**Endpoint**: `GET /api/v1/search/hpr`

**Parameters**: `hprId=HP-001`

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": 1000,
    "message": "Invalid request"
  }
}
```

### Common Error Codes

| Code | Message | Meaning |
|------|---------|---------|
| 1000 | Invalid request | Malformed request body |
| 1001 | Unauthorized | Invalid or expired token |
| 1002 | Forbidden | Insufficient permissions |
| 1003 | Not found | Resource doesn't exist |
| 1004 | Conflict | Duplicate entry |
| 1005 | Invalid state | Operation not allowed in current state |

## Examples

### Complete Consent Flow

```bash
# 1. Create Session
curl -X POST https://dev.abdm.gov.in/gateway/v0.5/sessions \
  -H "Content-Type: application/json" \
  -d '{"clientId":"YOUR_CLIENT_ID","clientSecret":"YOUR_SECRET"}'

# 2. Request Consent
curl -X POST https://dev.abdm.gov.in/gateway/v0.5/consent-requests/init \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-CM-ID: sbx" \
  -d @consent-request.json

# 3. Patient approves in ABHA app

# 4. Fetch Consent Artefact (after approval notification)
curl -X POST https://dev.abdm.gov.in/gateway/v0.5/consents/fetch \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-CM-ID: sbx" \
  -d '{"requestId":"unique-id","timestamp":"2024-03-01T14:00:00.000Z","consentId":"consent-id"}'

# 5. Request Health Information
curl -X POST https://dev.abdm.gov.in/gateway/v0.5/health-information/cm/request \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-CM-ID: sbx" \
  -d @health-info-request.json
```

### Testing with Webhook.site

```bash
# 1. Get webhook URL: https://webhook.site/
# 2. Register it as callback
curl -X PATCH https://dev.abdm.gov.in/devservice/v1/bridges \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"url":"https://webhook.site/your-unique-id"}'

# 3. Make API calls and observe callbacks at webhook.site
```

## API Specification Files

All OpenAPI/Swagger specifications are available:

- **Gateway**: `../api-schemas/gateway.yaml`
- **Consent Manager**: `../api-schemas/consent-manager.yaml`
- **HIP**: `../api-schemas/hip.yaml`
- **HIU**: `../api-schemas/hiu.yaml`
- **ABHA Service**: `../api-schemas/abha-service.yaml`

## Rate Limits

- **Sandbox**: 100 requests/minute per Client ID
- **Production**: Varies by service tier

## Support

- **Developer Forum**: https://devforum.abdm.gov.in/
- **Documentation**: https://sandbox.abdm.gov.in/docs

---

*Last Updated: 2026-02-14*
*API Version: v0.5*
