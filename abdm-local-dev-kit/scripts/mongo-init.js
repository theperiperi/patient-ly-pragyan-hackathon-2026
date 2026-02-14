// MongoDB initialization script for ABDM Local Dev Kit
// This script creates collections and indexes for optimal performance

db = db.getSiblingDB('abdm');

// Create collections with validation schemas
// Note: Patients collection stores FHIR Patient resources
// Schema validates FHIR R4 Patient structure with ABHA number
db.createCollection('patients', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['resourceType', 'abha_number', 'name', 'gender', 'birthDate'],
      properties: {
        resourceType: {
          bsonType: 'string',
          enum: ['Patient'],
          description: 'Must be Patient for FHIR Patient resources'
        },
        abha_number: {
          bsonType: 'string',
          pattern: '^[0-9]{2}-[0-9]{4}-[0-9]{4}-[0-9]{4}$',
          description: 'ABHA number in format XX-XXXX-XXXX-XXXX'
        },
        name: {
          bsonType: 'array',
          minItems: 1,
          items: {
            bsonType: 'object',
            required: ['text'],
            properties: {
              text: { bsonType: 'string' },
              given: {
                bsonType: 'array',
                items: { bsonType: 'string' }
              },
              family: { bsonType: 'string' }
            }
          },
          description: 'FHIR HumanName array - must have at least one name'
        },
        gender: {
          bsonType: 'string',
          enum: ['male', 'female', 'other', 'unknown'],
          description: 'FHIR AdministrativeGender code'
        },
        birthDate: {
          bsonType: 'string',
          pattern: '^[0-9]{4}-[0-9]{2}-[0-9]{2}$',
          description: 'Birth date in YYYY-MM-DD format'
        },
        identifier: {
          bsonType: 'array',
          description: 'FHIR Identifier array including ABHA'
        },
        telecom: {
          bsonType: 'array',
          description: 'FHIR ContactPoint array for phone/email'
        },
        address: {
          bsonType: 'array',
          description: 'FHIR Address array'
        }
      }
    }
  }
});

db.createCollection('practitioners');
db.createCollection('organizations');
db.createCollection('consent_requests');
db.createCollection('consent_artefacts');
db.createCollection('health_information_bundles');
db.createCollection('sessions');
db.createCollection('transaction_logs');
db.createCollection('care_contexts');

// Create indexes for patients
db.patients.createIndex({ 'abha_number': 1 }, { unique: true });
db.patients.createIndex({ 'identifier.value': 1 });
db.patients.createIndex({ 'telecom.value': 1 });
db.patients.createIndex({ 'name.text': 'text' });
db.patients.createIndex({ 'created_at': -1 });

// Create indexes for practitioners
db.practitioners.createIndex({ 'identifier.value': 1 }, { unique: true });
db.practitioners.createIndex({ 'name.text': 'text' });

// Create indexes for organizations
db.organizations.createIndex({ 'identifier.value': 1 }, { unique: true });
db.organizations.createIndex({ 'name': 'text' });

// Create indexes for consent requests
db.consent_requests.createIndex({ 'request_id': 1 }, { unique: true });
db.consent_requests.createIndex({ 'patient_abha': 1 });
db.consent_requests.createIndex({ 'status': 1 });
db.consent_requests.createIndex({ 'created_at': -1 });
db.consent_requests.createIndex({ 'hiu_id': 1 });

// Create indexes for consent artefacts
db.consent_artefacts.createIndex({ 'consent_id': 1 }, { unique: true });
db.consent_artefacts.createIndex({ 'consent_request_id': 1 });
db.consent_artefacts.createIndex({ 'patient_abha': 1 });
db.consent_artefacts.createIndex({ 'status': 1 });
db.consent_artefacts.createIndex({ 'expiry_date': 1 });

// Create indexes for health information bundles
db.health_information_bundles.createIndex({ 'bundle_id': 1 }, { unique: true });
db.health_information_bundles.createIndex({ 'patient_abha': 1 });
db.health_information_bundles.createIndex({ 'hip_id': 1 });
db.health_information_bundles.createIndex({ 'bundle_type': 1 });
db.health_information_bundles.createIndex({ 'created_at': -1 });

// Create indexes for sessions
db.sessions.createIndex({ 'access_token': 1 }, { unique: true });
db.sessions.createIndex({ 'client_id': 1 });
db.sessions.createIndex({ 'expires_at': 1 }, { expireAfterSeconds: 0 });

// Create indexes for transaction logs
db.transaction_logs.createIndex({ 'transaction_id': 1 }, { unique: true });
db.transaction_logs.createIndex({ 'request_id': 1 });
db.transaction_logs.createIndex({ 'timestamp': -1 });
db.transaction_logs.createIndex({ 'service': 1 });

// Create indexes for care contexts
db.care_contexts.createIndex({ 'link_reference': 1 }, { unique: true });
db.care_contexts.createIndex({ 'patient_abha': 1 });
db.care_contexts.createIndex({ 'hip_id': 1 });
db.care_contexts.createIndex({ 'status': 1 });

// Insert demo client credentials
db.sessions.insertOne({
  client_id: 'sandbox-client',
  client_secret: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIj.KkOzO6', // hashed 'sandbox-secret'
  name: 'Demo Client',
  created_at: new Date(),
  is_active: true
});

print('ABDM database initialized successfully!');
print('Collections created: patients, practitioners, organizations, consent_requests, consent_artefacts, health_information_bundles, sessions, transaction_logs, care_contexts');
print('Indexes created for optimal query performance');
print('Demo client credentials: sandbox-client / sandbox-secret');
